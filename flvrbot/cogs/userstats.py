import logging
import discord
from discord.ext import commands
from flvrbot.db import DBManager
import pytz
import traceback

logger = logging.getLogger(__name__)

class UserStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("UserStatsCog has been loaded")
        await self.add_guild_users_to_db()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = message.guild.id
        user_id = message.author.id
        joined_guild = message.author.joined_at.replace(tzinfo=pytz.UTC)

        if not message.author.bot:  # It's a good practice to skip bots
            existing_users = self.db_manager.get_users(guild_id, user_id)
            if not existing_users:  # This checks if the list is empty
                self.db_manager.add_user(guild_id=guild_id, user_id=user_id, joined_guild=joined_guild)

        message_content = ""
        if message.content:
            message_content = message.content

        module = "user"
        data = {
            "messages": 1,
            "characters": len(message_content)
        }

        self.db_manager.update_stats(guild_id=guild_id, user_id=user_id, module=module, data=data)
        self.db_manager.update_user(guild_id=guild_id, user_id=user_id, last_seen=message.created_at)

    @commands.slash_command(name="top10", description="Displays top 10 statistics for a specified module and sort_by option.")
    async def top10(
        self,
        ctx: discord.ApplicationContext,
        module: discord.Option(str, description="Enter module to view stats", required=False, default='user'), # type: ignore
        sort_by: discord.Option(str, description="How to sort the stats", required=False, default='messages') # type: ignore
    ):
        valid_modules = self.db_manager.get_valid_modules_and_sort_options()
        if module not in valid_modules:
            valid_module_keys = ", ".join(valid_modules.keys())
            await ctx.respond(f"Error, unsupported module. Try again! Valid choices are: {valid_module_keys}", ephemeral=True)
            return

        if sort_by not in valid_modules[module]:
            valid_sorts = ", ".join(valid_modules[module])
            await ctx.respond(f"Invalid sort_by option. Valid sort_by options for {module} are: {valid_sorts}", ephemeral=True)
            return

        guild_id = ctx.guild.id
        stats_data = self.db_manager.get_stats(guild_id, module)
        if not stats_data:
            await ctx.respond("No statistics found for the specified module.", ephemeral=True)
            return

        sorted_stats = sorted(
            stats_data.items(),
            key=lambda x: x[1].get(sort_by, 0),
            reverse=True
        )[:10]  # Limit to top 10

        if not sorted_stats:
            await ctx.respond("No data available for sorting.", ephemeral=True)
            return

        result_message = f"Top 10 Statistics for **{module}** sorted by **{sort_by}**: "
        result_message += "  ".join(f"**{index}. <@{user_id}>**: {stats.get(sort_by, 0)}" for index, (user_id, stats) in enumerate(sorted_stats, start=1))

        await ctx.respond(result_message)


    async def add_guild_users_to_db(self):
        logger.info("Adding guild users to the database...")
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:  # It's a good practice to skip bots
                    existing_users = self.db_manager.get_users(guild.id, member.id)
                    if not existing_users:  # This checks if the list is empty
                        joined_guild = member.joined_at.replace(tzinfo=pytz.UTC)
                        self.db_manager.add_user(guild_id=guild.id, user_id=member.id, joined_guild=joined_guild)
        logger.info("Guild users added to the database successfully.")

    @commands.slash_command(name="seen", description="Check when was the last time a user was seen.")
    async def seen(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(discord.Member, description="Select a user to check") # type: ignore
    ):
        guild_id = ctx.guild.id
        user_id = user.id

        try:
            logger.debug(f"{ctx.author.name} requested to check when {user_id} was last seen")

            # Retrieve user's last seen and last message
            user_data = self.db_manager.get_users(guild_id=guild_id, user_id=user_id)
            logger.debug(f"User data: {user_data}")

            if user_data:
                # Since user_data uses DB ids as keys, find the correct entry by user_id
                user_entry = next((details for data, details in user_data.items() if details['user_id'] == user_id), None)
                if user_entry:
                    last_seen = user_entry['last_seen']
                    if last_seen:
                        last_seen_formatted = last_seen.strftime("%B %d, %Y at %I:%M %p UTC")
                        message_content = f"I last saw {user.mention} on {last_seen_formatted}."
                        await ctx.respond(message_content)
                    else:
                        await ctx.respond(f"I haven't seen {user.mention} before.", ephemeral=True)
                else:
                    await ctx.respond(f"No data found for {user.mention}.", ephemeral=True)
            else:
                await ctx.respond(f"No data found for {user.mention}.", ephemeral=True)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            traceback.print_exc()



def setup(bot):
    bot.add_cog(UserStatsCog(bot))

