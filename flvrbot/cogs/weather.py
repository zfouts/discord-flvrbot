import json
import discord
from discord.ext import commands
import requests
import asyncio
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

weather_emojis = {
    "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️",
    "Thunderstorm": "⛈️", "Snow": "❄️", "Mist": "🌫️", "Smoke": "🌫️",
    "Haze": "🌫️", "Dust": "🌫️", "Fog": "🌫️", "Sand": "🌫️",
    "Ash": "🌫️", "Squall": "🌫️", "Tornado": "🌪️"
}

class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.weather_api_key = os.getenv('OPENWEATHER_APIKEY')
        self.maps_api_key = os.getenv('GOOGLE_MAPS_APIKEY')

        if not self.weather_api_key or not self.maps_api_key:
            logger.error("API keys are missing")
            raise RuntimeError("API keys not found in environment variables")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Weather Cog has been loaded.")

    @commands.slash_command(
        name="weather",
        description="Gets weather information for a given location"
    )
    async def weather(self, ctx, location: discord.Option(str, "Enter the location")): # type: ignore
        logger.debug(f"Received message location: {location}")
        try:
            lat, lon, address = await self.get_lat_lon(location)
            if lat is None or lon is None:
                await ctx.respond("Could not find the location specified. Please check the location and try again.")
                return

            weather_data = await self.fetch_weather(lat, lon)
            if weather_data:
                response = self.format_weather_response(weather_data, address)
                await ctx.respond(response)
            else:
                await ctx.respond("Failed to retrieve weather data. Please try again later.")

        except discord.NotFound:
            await ctx.respond("Message or channel not found in the specified channel.")
        except discord.Forbidden:
            await ctx.respond("Bot does not have the necessary permissions to perform this action.")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            await ctx.respond("An unexpected error occurred. Please contact the server administrator.")

    async def get_lat_lon(self, location):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={self.maps_api_key}"
        try:
            response = await self.make_async_request(url)
            data = response.json()
            if response.status_code == 200 and data['status'] == 'OK':
                result = data['results'][0]
                return result['geometry']['location']['lat'], result['geometry']['location']['lng'], result['formatted_address']
            else:
                logger.error(f"Geocode error: {data['status']} - {data.get('error_message', '')}")
                return None, None, None
        except requests.RequestException as e:
            logger.error(f"Request error during geocoding: {str(e)}")
            return None, None, None

    async def fetch_weather(self, lat, lon):
        api_version = os.getenv("WEATHER_API_VERSION", "2.5")
        base_url = "https://api.openweathermap.org/data/"
        endpoint = "onecall"

        url = f"{base_url}{api_version}/{endpoint}?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={self.weather_api_key}&units=metric"
        try:
            response = await self.make_async_request(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HTTP Error {response.status_code} for weather API")
                message = response.json()
                logger.error(f"Output: {message['message']}")
                return None
        except requests.RequestException as e:
            logger.error(f"Request error during weather data fetch: {str(e)}")
            return None

    async def make_async_request(self, url):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, requests.get, url)

    def deg_to_compass(self, num):
        val = int((num / 22.5) + 0.5)
        compass_points = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        return compass_points[(val % 16)]

    def format_weather_response(self, data, location):
        owm_timezone = data['timezone']
        current = data['current']
        temp = current['temp']
        feels_like = current['feels_like']
        description = current['weather'][0]['description'].capitalize()

        main_weather = current['weather'][0]['main']
        emoji = weather_emojis.get(main_weather, "🌞")

        sunrise = self.format_time(current['sunrise'], data['timezone_offset'])
        sunset = self.format_time(current['sunset'], data['timezone_offset'])
        daylight_hours = self.calculate_daylight_hours(current['sunrise'], current['sunset'])

        wind_speed_metric, wind_speed_imperial = self.format_wind_speed(current['wind_speed'])
        wind_gust_metric, wind_gust_imperial = self.format_wind_gust(current.get('wind_gust', 0))
        wind_direction = self.deg_to_compass(current['wind_deg'])

        humidity = current['humidity']
        clouds = current['clouds']

        today_summary = self.get_today_summary(data)
        wind_details = self.get_wind_details(wind_speed_metric, wind_speed_imperial, wind_gust_metric, wind_gust_imperial, wind_direction)
        rain_info = self.get_precipitation_info(current, 'rain')
        snow_info = self.get_precipitation_info(current, 'snow')
        alerts_info = self.get_alerts_info(data, data['timezone_offset'])

        response = (
            f"**Weather for {location}:**\n"
            f"{today_summary}"
            f"**Current Conditions:** {main_weather} - {description} {emoji}\n"
            f"**Temperature:** {temp * 9/5 + 32:.2f}°F / {temp}°C (Feels like: {feels_like * 9/5 + 32:.2f}°F / {feels_like}°C)\n"
            f"**Humidity:** {humidity}% **Clouds:** {clouds}%\n"
            f"{wind_details}\n"
            f"**Sunrise:** :sunrise: {sunrise}, **Sunset:** :sunset: {sunset} {owm_timezone} ({daylight_hours:.2f} hours of daylight)\n"
            f"{rain_info}{snow_info}"
            f"{alerts_info}"
        )
        return response

    def format_time(self, timestamp, offset):
        return datetime.fromtimestamp(timestamp + offset, timezone.utc).strftime('%I:%M %p')

    def calculate_daylight_hours(self, sunrise, sunset):
        daylight = datetime.fromtimestamp(sunset) - datetime.fromtimestamp(sunrise)
        return daylight.seconds / 3600

    def format_wind_speed(self, wind_speed):
        wind_speed_metric = f"{wind_speed * 3.6:.1f} km/h"
        wind_speed_imperial = f"{wind_speed * 2.237:.1f} mph"
        return wind_speed_metric, wind_speed_imperial

    def format_wind_gust(self, wind_gust):
        wind_gust_metric = f"{wind_gust * 3.6:.1f} km/h" if wind_gust else None
        wind_gust_imperial = f"{wind_gust * 2.237:.1f} mph" if wind_gust else None
        return wind_gust_metric, wind_gust_imperial

    def get_today_summary(self, data):
        if 'daily' in data:
            today = data['daily'][0]
            today_summary = today['weather'][0]['description'].capitalize()
            today_high = today['temp']['max']
            return f"**Forecast**: {today_summary} with a high around {today_high * 9/5 + 32:.2f}°F / {today_high}°C\n"
        return ""

    def get_wind_details(self, wind_speed_metric, wind_speed_imperial, wind_gust_metric, wind_gust_imperial, wind_direction):
        wind_details = f"**Wind:** {wind_speed_imperial} / {wind_speed_metric}, {wind_direction}"
        if wind_gust_metric:
            wind_details += f", Gusting to {wind_gust_imperial} / {wind_gust_metric}"
        return wind_details

    def get_precipitation_info(self, current, precipitation_type):
        if precipitation_type in current and '1h' in current[precipitation_type]:
            precipitation_mm = current[precipitation_type]['1h']
            precipitation_inches = precipitation_mm * 0.0393701
            return f"**{precipitation_type.capitalize()}**: {precipitation_inches:.2f} inches / {precipitation_mm:.2f} mm per hour\n"
        return ""

    def get_alerts_info(self, data, timezone_offset):
        if 'alerts' in data:
            alerts = data['alerts'][0]
            alerts_sender_name = alerts['sender_name']
            alerts_event = alerts['event']
            alerts_start = self.format_time(alerts['start'], timezone_offset)
            alerts_end = self.format_time(alerts['end'], timezone_offset)
            alerts_description = alerts['description']
            return (
                f":warning:**{alerts_event}**:warning:\n"
                f"{alerts_sender_name} has issued a {alerts_event} at {alerts_start} until {alerts_end}\n"
                f"{alerts_description}\n"
            )
        return ""

def setup(bot):
    bot.add_cog(WeatherCog(bot))

