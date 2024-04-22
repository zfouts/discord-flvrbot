# flvrbot/bot.py

import discord
from discord.ext import commands
import logging
from flvrbot import load_cogs
from flvrbot.db import DBManager
import pytz

class FlvrBot(commands.Bot):
    def __init__(self, token=None, command_prefix='!', description=None):
        if token is None:
            raise ValueError("Token is required")

        self.logger = logging.getLogger(__name__)

        # Setup Discord
        self.token = token
        intents = discord.Intents.all()
        super().__init__(command_prefix=command_prefix, description=description, intents=intents)

        # Setup DBManager
        self.db_manager = DBManager()

        # Load cogs
        load_cogs.setup(self)

        @self.event
        async def on_ready():
            self.logger.info(f'Logged in as {self.user}')

        """
        # Handle errors
        @self.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send('That command does not exist.')
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('You are missing a required argument.')
            elif isinstance(error, commands.CheckFailure):
                await ctx.send("You don't have the necessary permissions to use this command.")
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(f"This command is on cooldown. Please wait {error.retry_after:.2f} seconds.")
            else:
                # Generic error message for unexpected errors
                await ctx.send(f'An unexpected error occurred: {error}')
                self.logger.error(f'An unexpected error occurred: {error}')
        """

    def run(self):
        super().run(self.token)

