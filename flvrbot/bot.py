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

        # You've logged in! Adding all guild members to the users db.
        @self.event
        async def on_ready():
            self.logger.info(f'Logged in as {self.user}')
            await self.add_guild_users_to_db()
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

    # Record the guild members, this is used for cogs.
    async def add_guild_users_to_db(self):
        self.logger.info("Adding guild users to the database...")
        for guild in self.guilds:
            for member in guild.members:
                if not member.bot:  # It's a good practice to skip bots
                    existing_users = self.db_manager.get_users(guild.id, member.id)
                    if not existing_users:  # This checks if the list is empty
                        joined_guild = member.joined_at.replace(tzinfo=pytz.UTC)
                        self.db_manager.add_user(guild_id=guild.id, user_id=member.id, display_name=member.display_name, joined_guild=joined_guild)
        self.logger.info("Guild users added to the database successfully.")

    def run(self):
        super().run(self.token)

