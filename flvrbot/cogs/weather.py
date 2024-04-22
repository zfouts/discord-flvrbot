import json
import discord
from discord.ext import commands
import requests
import asyncio
import logging
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

weather_emojis = {
    "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️", "Drizzle": "🌦️",
    "Thunderstorm": "⛈️", "Snow": "❄️", "Mist": "🌫️", "Smoke": "🌫️",
    "Haze": "🌫️", "Dust": "🌫️", "Fog": "🌫️", "Sand": "🌫️",
    "Ash": "🌫️", "Squall": "🌫️", "Tornado": "🌪️"
}

class WeatherCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Weather Cog has been loaded.")
        self.weather_api_key = os.getenv('OPENWEATHER_APIKEY')
        self.maps_api_key = os.getenv('GOOGLE_MAPS_APIKEY')

        if not self.weather_api_key or not self.maps_api_key:
            logger.error("API keys are missing")
            raise RuntimeError("API keys not found in environment variables")

    @commands.slash_command(
        name="weather",
        description="Configure reaction roles for the server.",
        help="Gets weather information for a given location"
    )
    async def weather(self, ctx, location: discord.Option(str, "Enter the location")): # type: ignore
        logger.debug(f"Received message location: {location}")
        try:
            logger.info(f"Received request for weather with location: {location}")
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
            logger.error(f"An unexpected error occurred: {e}")
            await ctx.respond("An unexpected error occurred. Please contact the server administrator.")

    async def get_lat_lon(self, location):
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={self.maps_api_key}"
        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(None, requests.get, url)
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

        loop = asyncio.get_running_loop()
        try:
            response = await loop.run_in_executor(None, requests.get, url)
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
        sunrise = datetime.fromtimestamp(current['sunrise'] + data['timezone_offset'], timezone.utc).strftime('%I:%M %p')
        sunset = datetime.fromtimestamp(current['sunset'] + data['timezone_offset'], timezone.utc).strftime('%I:%M %p')
        daylight = datetime.fromtimestamp(current['sunset']) - datetime.fromtimestamp(current['sunrise'])
        daylight_hours = daylight.seconds / 3600

        wind_speed_metric = f"{current['wind_speed'] * 3.6:.1f} km/h"
        wind_speed_imperial = f"{current['wind_speed'] * 2.237:.1f} mph"
        wind_gust_metric = f"{current.get('wind_gust', 0) * 3.6:.1f} km/h" if 'wind_gust' in current else None
        wind_gust_imperial = f"{current.get('wind_gust', 0) * 2.237:.1f} mph" if 'wind_gust' in current else None
        wind_direction = self.deg_to_compass(current['wind_deg'])
        humidity = current['humidity']
        clouds = current['clouds']


        today_summary = ""
        if 'daily' in data:
            today = data['daily'][0]
            today_summary = today['weather'][0]['description'].capitalize()
            today_high = today['temp']['max']
            today_summary = f"**Forecast**: {today_summary} with a high around {today_high * 9/5 + 32:.2f}°F / {today_high}°C\n"

        wind_details = f"**Wind:** {wind_speed_imperial} / {wind_speed_metric}, {wind_direction}"
        if wind_gust_metric:
            wind_details += f", Gusting to {wind_gust_imperial} / {wind_gust_metric}"

        rain_info = ""
        if 'rain' in current and '1h' in current['rain']:
            rain_mm = current['rain']['1h']
            rain_inches = rain_mm * 0.0393701
            rain_info = f"**Rain:** {rain_inches:.2f} inches / {rain_mm:.2f} mm per hour\n"

        snow_info = ""
        if 'snow' in current and '1h' in current['snow']:
            snow_mm = current['snow']['1h']
            snow_inches = snow_mm * 0.0393701
            snow_info = f"**Snow:** {snow_inches:.2f} in / {snow_mm:.2f} mm per hour\n"

        alerts_info = ""
        if 'alerts' in data:
            try:
                alerts_sender_name = data['alerts']['sender_name']
                alerts_event = data['alerts']['event']
                alerts_start = datetime.fromtimestamp(data['alerts']['start'] + current['timezone_offset'], timezone.utc).strftime('%I:%M %p')
                alerts_end = datetime.fromtimestamp(data['alerts']['end'] + current['timezone_offset'], timezone.utc).strftime('%I:%M %p')
                alerts_description = data['alerts']['description']
                alerts_info = (
                    f":warning:**{alerts_event}**:warning:\n"
                    f"{alerts_sender_name} has issued a {alerts_event} at {alerts_start} until {alerts_end}"
                    f"{alerts_description}"
                )
            except:
                pass

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

def setup(bot):
    bot.add_cog(WeatherCog(bot))






