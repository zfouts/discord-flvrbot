import discord
from discord.ext import commands
import logging
import random

class MockCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Mock module has been loaded")

    @discord.slash_command(name="mock", description="Automatic spongebob-mocking-text")
    async def mock(
        self, 
        ctx: discord.ApplicationContext, 
        mockstring: discord.Option(str, description="Enter the string to mock")
    ):
        lower_string = mockstring.lower()
        output_text = ""
        counter = 0
        for char in lower_string:
            if char != ' ':
                counter += 1
            if counter % 2 == 0:
                output_text += char.lower()
            else:
                output_text += char.upper()
        await ctx.respond(output_text)

def setup(bot):
    bot.add_cog(MockCog(bot))

