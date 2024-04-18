# cogs/user_stats.py
import logging
from discord.ext import commands
from flvrbot.db import DBManager

logger = logging.getLogger(__name__)

class UserStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("User Stats module has been loaded")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = message.guild.id
        user_id = message.author.id

        module = "user"
        # Update user stats
        data = {
            "messages": 1,
            "characters": len(message.content)
        }
        self.db_manager.update_stats(guild_id=guild_id, user_id=user_id, module=module, data=data)
        self.db_manager.update_user(guild_id=guild_id, user_id=user_id, last_seen=message.created_at, last_message=message.content)

    @commands.command(help="Displays top 10 stats for the specified module for each user in the guild, sorted by characters count. Defaults to 'user' module.")
    async def top10(self, ctx, module=None):
        if not module:
            module = 'user'

        guild_id = ctx.guild.id

        users_with_stats = self.db_manager.get_users_with_stats(guild_id, module)  # Fetch users with stats recorded for the guild and module

        top10_users = []
        for user in users_with_stats:
            stats = self.db_manager.get_stats(guild_id, user.user_id, module)  # Fetch stats for the user and module
            if 'characters' in stats:
                top10_users.append((user, stats['characters']))  # Append user and character count to list

        top10_users.sort(key=lambda x: x[1], reverse=True)  # Sort users by character count in descending order
        top10_users = top10_users[:10]  # Take top 10 users

        output = ""
        for user, characters_count in top10_users:
            output += f"{user.display_name}: {characters_count} characters\n"

        await ctx.send(f"Top 10 {module.capitalize()} Stats for each user in the guild, sorted by character count:\n{output}")




def setup(bot):
    bot.add_cog(UserStats(bot))


