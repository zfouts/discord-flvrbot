import discord
from discord.ext import commands
import aiohttp  # For asynchronous HTTP requests
import logging

class CurrencyConverter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_url = "https://api.exchangerate-api.com/v4/latest/"
        self.logger = logging.getLogger(__name__)  # Define a logger

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Currency module has been loaded")

    @commands.slash_command(name="currency", description="Converts currency")
    async def currency(
        self,
        ctx: discord.ApplicationContext,
        value: discord.Option(float, description="Value", required=True),  # Change type to float
        currency1: discord.Option(str, description="Currency From", required=True),  # Change type to str
        currency2: discord.Option(str, description="Currency To", required=True)  # Change type to str
        ):
        async with aiohttp.ClientSession() as session:  # Use aiohttp for asynchronous requests
            async with session.get(f"{self.api_url}{currency1.upper()}") as response:
                if response.status != 200:
                    await ctx.respond("Failed to retrieve currency data. Please check the currency codes.")
                    return
                data = await response.json()
                rates = data.get("rates", {})
                rate_to = rates.get(currency2.upper())

                if rate_to:
                    converted_value = value * rate_to
                    await ctx.respond(f"{value} {currency1.upper()} is {converted_value:.2f} {currency2.upper()}")
                else:
                    await ctx.respond(f"Conversion rate for {currency2.upper()} not found.")

def setup(bot):
    bot.add_cog(CurrencyConverter(bot))

