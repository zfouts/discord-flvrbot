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
            await self.add_guild_users_to_db()

    # Record the guild members, this is used for cogs.
    async def add_guild_users_to_db(self):
        self.logger.info("Adding guild users to the database...")
        for guild in self.guilds:
            for member in guild.members:
                # Check if the user already exists in the database
                existing_user = self.db_manager.get_users(guild.id, member.id)
                if not existing_user:
                    joined_guild = member.joined_at.replace(tzinfo=pytz.UTC)
                    self.db_manager.add_user(guild_id=guild.id, user_id=member.id, display_name=member.display_name, joined_guild=joined_guild)
        self.logger.info("Guild users added to the database successfully.")

    def run(self):
        super().run(self.token)

