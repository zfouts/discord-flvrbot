# main.py
import logging
import os
import sys
from dotenv import load_dotenv
from flvrbot.bot import FlvrBot

def setup_logging():
    log_level_str = os.environ.get('LOG_LEVEL', "DEBUG").upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(stream=sys.stdout, level=log_level_str, format=log_format)

def load_env():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

def main():
    load_env()
    setup_logging()
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("Error: Discord token not found in environment variable 'DISCORD_TOKEN'")
        return
    bot = FlvrBot(token=token)
    bot.run()

if __name__ == "__main__":
    main()

