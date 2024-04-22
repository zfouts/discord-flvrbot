
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

        module = "user"
        data = {
            "messages": 1,
            "characters": len(message.content)
        }
        self.db_manager.update_stats(guild_id=guild_id, user_id=user_id, module=module, data=data)
        self.db_manager.update_user(guild_id=guild_id, user_id=user_id, last_seen=message.created_at, last_message=message.content)

    @commands.slash_command(name="top10", description="Displays top 10 statistics for a specified module and sort_by option.")
    async def top10(
        self,
        ctx: discord.ApplicationContext,
        module: discord.Option(str, description="Enter module to view stats", required=False, default='user'), # type: ignore
        sort_by: discord.Option(str, description="How to sort the stats", required=False, default='characters') # type: ignore
    ):
        valid_modules = self.db_manager.get_valid_modules_and_sort_options()
        if module not in valid_modules:
            valid_module_keys = ", ".join(valid_modules.keys())
            await ctx.respond(f"Error, unsupported module. Try again! Valid choices are: {valid_module_keys}")
            return

        if sort_by not in valid_modules[module]:
            valid_sorts = ", ".join(valid_modules[module])
            await ctx.respond(f"Invalid sort_by option. Valid sort_by options for {module} are: {valid_sorts}")
            return

        guild_id = ctx.guild.id
        stats_data = self.db_manager.get_stats(guild_id, module)
        if not stats_data:
            await ctx.respond("No statistics found for the specified module.")
            return

        sorted_stats = sorted(
            stats_data.items(),
            key=lambda x: x[1].get(sort_by, 0),
            reverse=True
        )[:10]  # Limit to top 10

        if not sorted_stats:
            await ctx.respond("No data available for sorting.")
            return

        """
        # Old method
        result_message = f"Top 10 Statistics for **{module}** sorted by **{sort_by}**: "
        result_message += "  ".join(f"**{index}. <@{user_id}>**: {stats.get(sort_by, 0)}" for index, (user_id, stats) in enumerate(sorted_stats, start=1))
        """

        embed = discord.Embed(title=f"Top 10 Statistics for {module}", description=f"Sorted by {sort_by}", color=discord.Color.blue())
        for index, (user_id, stats) in enumerate(sorted_stats, start=1):
            user_name = self.bot.get_user(user_id)
            user_name = user_name.display_name if user_name else f"UserID {user_id}"
            embed.add_field(name=f"{index}. {user_name}", value=f"{stats.get(sort_by, 0)}", inline=False)

        await ctx.respond(embed=embed)

    async def add_guild_users_to_db(self):
        logger.info("Adding guild users to the database...")
        for guild in self.bot.guilds:
            for member in guild.members:
                if not member.bot:  # It's a good practice to skip bots
                    existing_users = self.db_manager.get_users(guild.id, member.id)
                    if not existing_users:  # This checks if the list is empty
                        joined_guild = member.joined_at.replace(tzinfo=pytz.UTC)
                        self.db_manager.add_user(guild_id=guild.id, user_id=member.id, display_name=member.display_name, joined_guild=joined_guild)
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
                last_seen = user_data.get('last_seen')
                last_message = user_data.get('last_message')

                if last_seen:
                    last_seen_formatted = last_seen.strftime("%B %d, %Y")
                    message_content = f"I last saw {user.mention} on {last_seen_formatted}."
                    if last_message:
                        message_content += f" They said: \"{last_message}\""
                    else:
                        message_content += " No message was recorded."
                    await ctx.respond(message_content)
                else:
                    await ctx.respond(f"I haven't seen {user.mention} before.")
            else:
                await ctx.respond(f"No data found for {user.mention}.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            traceback.print_exc()  # Print traceback to console for debugging

def setup(bot):
    bot.add_cog(UserStatsCog(bot))

