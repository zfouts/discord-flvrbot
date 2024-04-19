import logging
from discord.ext import commands
from flvrbot.db import DBManager
from datetime import datetime
import traceback
import discord

logger = logging.getLogger(__name__)

class SeenCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Seen module has been loaded")

    @commands.command(name="seen", help="Check when was the last time a user was seen.")
    async def seen(self, ctx, user: discord.Member):
        guild_id = ctx.guild.id

        try:
            user_id = user.id

            logger.debug(f"{ctx.author.name} called !seen {user_id}")

            # Retrieve user's last seen and last message
            user_data = self.db_manager.get_users(guild_id=guild_id, user_id=user_id)
            logger.debug(f"User data: {user_data}")

            if user_data:
                for key, data in user_data.items():
                    logger.debug(f"Processing data for user with key: {key}")
                    last_seen = data['last_seen']
                    last_message = data['last_message']

                    if last_message is not None:
                        last_message = str(last_message)  # Ensure last_message is a string

                    if last_seen:
                        last_seen_formatted = last_seen.strftime("%B %d, %Y")
                        message_content = f"I last saw {user.mention} on {last_seen_formatted}"
                        if last_message:
                            message_content += f" saying: \"{last_message}\""
                        else:
                            message_content += " but there was no recorded message."
                        await ctx.send(message_content)
                        return  # Exit the loop after sending the message
                else:
                    await ctx.send(f"I haven't seen {user.mention} before.")
            else:
                await ctx.send(f"No data found for {user.mention}.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            traceback.print_exc()  # Print traceback to console for debugging
            await ctx.send("An unexpected error occurred while processing the command.")



def setup(bot):
    bot.add_cog(SeenCog(bot))

