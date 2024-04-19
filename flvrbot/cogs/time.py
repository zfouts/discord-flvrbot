import discord
from discord.ext import commands
import pytz
from datetime import datetime
from dateutil import parser
from dateutil.relativedelta import relativedelta

class TimeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone_mapping = {
            "EST": "America/New_York",
            "EDT": "America/New_York",
            "CST": "America/Chicago",
            "CDT": "America/Chicago",
            "MST": "America/Denver",
            "MDT": "America/Denver",
            "PST": "America/Los_Angeles",
            "PDT": "America/Los_Angeles",
            "CET": "Europe/Paris",
            "CEST": "Europe/Paris",
            "GMT": "Etc/GMT",
            "UTC": "Etc/UTC",
            "BST": "Europe/London",  # British Summer Time
            "IST": "Europe/Dublin",  # Irish Standard Time
            "WET": "Europe/Lisbon",  # Western European Time
            "WEST": "Europe/Lisbon", # Western European Summer Time
            "EET": "Europe/Bucharest",  # Eastern European Time
            "EEST": "Europe/Bucharest", # Eastern European Summer Time
            "AST": "America/Halifax",  # Atlantic Standard Time
            "ADT": "America/Halifax",  # Atlantic Daylight Time
            "AKST": "America/Anchorage", # Alaska Standard Time
            "AKDT": "America/Anchorage", # Alaska Daylight Time
            "HST": "Pacific/Honolulu",  # Hawaii Standard Time
            "HAST": "Pacific/Honolulu", # Hawaii-Aleutian Standard Time (no daylight saving)
            "HADT": "America/Adak",     # Hawaii-Aleutian Daylight Time
            "AEST": "Australia/Sydney", # Australian Eastern Standard Time
            "AEDT": "Australia/Sydney", # Australian Eastern Daylight Time
            "ACST": "Australia/Darwin", # Australian Central Standard Time
            "ACDT": "Australia/Adelaide", # Australian Central Daylight Time
            "AWST": "Australia/Perth"   # Australian Western Standard Time
        }

    @commands.command(help="Displays the current time in a specified timezone. Example: !time America/Chicago")
    async def time(self, ctx, timezone='UTC'):
        # Check if the input timezone is in the mapping and convert it
        actual_timezone = self.timezone_mapping.get(timezone.upper(), timezone)

        try:
            current_time = datetime.now(pytz.timezone(actual_timezone))
        except pytz.exceptions.UnknownTimeZoneError:
            await ctx.send(f"Unknown timezone '{timezone}'. Please provide a valid timezone.")
            return

        time_24hr = current_time.strftime('%H:%M')
        time_12hr = current_time.strftime('%I:%M %p')
        response = (f"Current time in **{timezone}** ({actual_timezone}):\n"
                    f"24-hour format: {time_24hr}\n"
                    f"12-hour format: {time_12hr}")
        await ctx.send(response)

    @commands.command(help="Converts a given timestamp to a Unix timestamp and tells how long until that date. Example: !timeuntil '2024-04-20' or April 20th, 2024")
    async def timeuntil(self, ctx, *, time_string):
        try:
            # Parse the date string to datetime object
            target_time = parser.parse(time_string)
        except ValueError:
            await ctx.send("Invalid date format. Please provide a valid date.")
            return

        # Unix timestamp
        unix_timestamp = int(target_time.timestamp())
        # Calculate duration until the date
        now = datetime.now()
        if target_time > now:
            duration = relativedelta(target_time, now)
            time_until = f"{duration.years} years, {duration.months} months, {duration.days} days, {duration.hours} hours, {duration.minutes} minutes"
        else:
            time_until = "This date has already passed."

        response = (f"Unix timestamp: {unix_timestamp}\n"
                    f"Time until date: {time_until}")
        await ctx.send(response)

def setup(bot):
    bot.add_cog(TimeCog(bot))

