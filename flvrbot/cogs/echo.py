from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class EchoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("echo command module has been loaded")

    @commands.slash_command(name="echo", description="Echoes back your input")
    async def echo(ctx, input: str):
        await ctx.respond(input, ephemeral=True)

def setup(bot):
    bot.add_cog(EchoCog(bot))

