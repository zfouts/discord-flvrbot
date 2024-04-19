import logging
import os

logger = logging.getLogger(__name__)

class CogLoader:
    def __init__(self, bot):
        """
        Constructor method for CogLoader class.

        Args:
            bot: The Discord bot instance.
        """
        self.bot = bot

    def load_cogs(self):
        """
        Method to load all cogs.
        """
        logger.info("Loading cogs...")

        # Load built-in cogs
        predefined_cogs = [
            'flvrbot.cogs.basic',
            'flvrbot.cogs.unitconvert',
            'flvrbot.cogs.rekt',
            'flvrbot.cogs.decider',
            'flvrbot.cogs.roulette',
            'flvrbot.cogs.slap',
            'flvrbot.cogs.time',
            'flvrbot.cogs.weather',
            'flvrbot.cogs.userstats'
        ]
        for cog_name in predefined_cogs:
            try:
                self.bot.load_extension(cog_name)
                logger.info(f"Loaded cog module: {cog_name}")
            except Exception as e:
                logger.error(f"Failed to load cog module: {cog_name}. Error: {e}")

        # Check if /app/cogs directory exists -- this is for custom cogs.
        cogs_directory = '/app/cogs'
        if os.path.exists(cogs_directory) and os.path.isdir(cogs_directory):
            # Load cogs from /app/cogs directory dynamically
            for filename in os.listdir(cogs_directory):
                if filename.endswith('.py') and filename != '__init__.py':
                    cog_path = f'cogs.{filename[:-3]}'
                    logger.debug("Attempting to load cog module: %s", cog_path)
                    try:
                        self.bot.load_extension(cog_path)
                        logger.info(f"Loaded cog module: {cog_path}")
                    except Exception as e:
                        logger.error(f"Failed to load cog module: {cog_path}. Error: {e}")
        else:
            logger.info("Directory '/app/cogs' does not exist. No additional cogs loaded.")

def setup(bot):
    cog_loader = CogLoader(bot)
    cog_loader.load_cogs()

