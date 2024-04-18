# flvrbot/load_cogs.py

import logging

logger = logging.getLogger(__name__)

class CogLoader:
    def __init__(self, bot):
        self.bot = bot

    def load_cogs(self):
        logger.info("Loading cogs...")
        cogs_to_load = [
            'flvrbot.cogs.uptime',
            'flvrbot.cogs.unitconvert',
            'flvrbot.cogs.cooldown',
            'flvrbot.cogs.userstats'
        ]
        for cog_name in cogs_to_load:
            self.bot.load_extension(cog_name)
            logger.info(f"Loaded cog module: {cog_name}")

def setup(bot):
    cog_loader = CogLoader(bot)
    cog_loader.load_cogs()


