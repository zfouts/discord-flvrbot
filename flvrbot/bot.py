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
        intents = discord.Intents.default()
        #intents.guilds = True
        #intents.guild_members = True
        #intents.guild_messages = True
        #intents.message_content = True
        #intents.direct_messages = True

        super().__init__(command_prefix=command_prefix, description=description, intents=intents)

        # Setup DBManager
        self.db_manager = DBManager()

        # Load cogs
        load_cogs.setup(self)

        @self.event
        async def on_ready():
            self.logger.info(f'Logged in as {self.user}')

    def run(self):
        super().run(self.token)

