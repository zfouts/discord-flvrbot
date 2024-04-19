import logging
from discord.ext import commands
from flvrbot.db import DBManager
import json

logger = logging.getLogger(__name__)

class UserStatsCog(commands.Cog):
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

    @commands.command(name="top10", help="!top10 [module] [sort_by]")
    async def top10(self, ctx, module=None, sort_by=None):
        if module:
            valid_modules = self.db_manager.get_valid_modules_and_sort_options()
            if module not in valid_modules:
                valid_module_keys = ", ".join(valid_modules.keys())
                await ctx.send(f"Error, unsupported module. Try again! !top10 [{valid_module_keys}] are valid choices.")
                return
            
            if not sort_by:
                valid_sorts = ", ".join(valid_modules[module])
                await ctx.send(f"Please provide a sort_by parameter. Valid sort_by options for {module} are: {valid_sorts}")
                return

            if sort_by not in valid_modules[module]:
                valid_sorts = ", ".join(valid_modules[module])
                await ctx.send(f"Invalid sort_by option. Valid sort_by options for {module} are: {valid_sorts}")
                return

        else:
            # Default to user module and characters if no module is specified
            module = 'user'
            sort_by = 'characters'
        
        # Continue with data fetching and sorting logic
        guild_id = ctx.guild.id
        stats_data = self.db_manager.get_stats(guild_id, module)
        if not stats_data:
            await ctx.send("No statistics found for the specified module.")
            return

        sorted_stats = sorted(
            stats_data.items(),
            key=lambda x: x[1].get(sort_by, 0),
            reverse=True
        )[:10]  # Limit to top 10

        if not sorted_stats:
            await ctx.send("No data available for sorting.")
            return

        result_message = f"Top 10 Statistics for **{module}** sorted by **{sort_by}**: "
        result_message += "  ".join(f"**{index}. <@{user_id}>**: {stats.get(sort_by, 0)}" for index, (user_id, stats) in enumerate(sorted_stats, start=1))

        await ctx.send(result_message)

def setup(bot):
    bot.add_cog(UserStatsCog(bot))

