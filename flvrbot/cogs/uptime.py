# cogs/uptime.py

import discord
import logging
from discord.ext import commands
from datetime import datetime

logger = logging.getLogger(__name__)

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()

    @commands.Cog.listener()
    async def on_ready(self):
        print('Module load')
        logger.info("Uptime module has been loaded")

    def has_admin_role(self, user):
        return any(role.name.lower() == "admin" for role in user.roles)

    @commands.command(help="Displays how long the bot has been running. Admin role required.")
    async def uptime(self, ctx):
        if self.has_admin_role(ctx.author):
            uptime = datetime.utcnow() - self.start_time
            human_readable = str(uptime).split(".")[0]
            await ctx.send(f"I have been online for {human_readable}")
        else:
            await ctx.send("You need to have the Admin role to use this command.")

def setup(bot):
    bot.add_cog(Uptime(bot))


