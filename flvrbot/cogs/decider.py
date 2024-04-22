import discord
from discord.ext import commands
import random
import re
import logging

logger = logging.getLogger(__name__)

class DeciderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.should_options = ["Yes", "No", "Maybe"]


    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Decider module has been loaded")
    #
    # Eightball Command
    #
    @discord.slash_command(name="8ball", description="Return an 8-ball response.")
    async def info(
        self,
        ctx: discord.ApplicationContext): # type: ignore
        answers = [
            "Ask Again Later",
            "Better Not Tell You Now",
            "Concentrate and Ask Again",
            "Don't Count on It",
            "It Is Certain",
            "Most Likely",
            "My Reply is No",
            "My Sources Say No",
            "No",
            "Outlook Good",
            "Outlook Not So Good",
            "Reply Hazy, Try Again",
            "Signs Point to Yes",
            "Yes",
            "Yes, Definitely",
            "You May Rely On It",
        ]
        await ctx.respond(":8ball:" + random.choice(answers))



def setup(bot):
    bot.add_cog(DeciderCog(bot))

