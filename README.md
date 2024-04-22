# FlvrBot

FlvrBot is a Discord bot designed to provide various useful features to your server.

## Features

TODO: Add more information about features.

## Installation

To use FlvrBot in your Discord server, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies using `pip install .`.
3. Set up a `.env` file with your Discord bot token and any other necessary environment variables.
4. See the example on how to run the bot with `example/main.py`.
5. With `example/main.py` if you create a `cogs` folder you can load your own custom cogs without needing to modify any core files. See the `docker-compose.yml` file for an example of how it works.


See [Dockerfile](https://github.com/zfouts/discord-flvrbot/blob/main/Dockerfile) if you wish to see how it is ran in Docker or [docker-compose.yml](https://github.com/zfouts/discord-flvrbot/blob/main/docker-compose.yml) to run with docker-compose.


## Available Commands

- `/8ball`: Returns an 8-ball response. Example: `/eightball`
- `/rekt`: Rekts another user. Example: `/rekt <@username>`.
- `/roulette`: Plays a game of Russian Roulette. Example: `/roulette`.
- `/seen`: Check when was the last time a user was seen. Example: `/seen @flvrtown`.
- `/slap`: Slap someone in the channel. If no one is mentioned, a random person is slapped. Example: `/slap @flvrtown`.
- `/time`: Displays the current time in a specified timezone. Example: `/time <timezone>`.
- `/timeuntil`: Converts a given timestamp to a Unix timestamp and tells how long until that time. Example: `/timeuntil April 20, 2025 4:20pm` or `/timeuntil 04/20/25 4:20PM`.
- `/convert`: Converts units. Usage: `/convert <value> <from_unit> <to_unit>`. Utilizes the [Pint](https://pint.readthedocs.io/en/stable/) library.
- `/top10`: Shows the top 10 users by various metrics. Usage: `/top10 [module] [sort_by]`. By default `[module] is set to `user` and `[sort_by]` is set to `characters` if no input provided.
- `/weather`: Gets weather information for a given location. Uses [OpenWeatherMap][https://openweathermap.org/] and [Google Maps](https://developers.google.com/maps/documentation/). Example: `/w Austin, TX` or `/weather 78702`.
- `/uptime`: Shows how long the bot has been running.

Notes: 
- `/uptime`: hidden from the /help column, but is restricted to only users on the guild who have an administrator privilege. .


### Included Custom Example Commands

These are included as examples, but not enabled by default. Requires restricted intents to use.
See `examples/cogs`:

- `/seen`: Not enabled by default, this is located in `examples/cogs/seen.py`. Please see `examples/cogs/` for how you can setup your custom cogs.
- `/top10`: Shows the top 10 users by various metrics. Usage: `/top10 [module] [sort_by]`. By default `[module] is set to `user` and `[sort_by]` is set to `characters` if no input provided.


## Environment variables

Currently, this bot uses a few variables:

- `DISCORD_TOKEN`: This is the token you receive from Discord. Default: None.
- `DB_URL`: This is a SQLAlchemy database URL string. Default: `sqlite:////tmp/flvrbot.db`. Supports postgres out of the box. You can look at `docker-compose.yml` to see an example of using postgres.
- `OPENWEATHER_APIKEY`: API key for accessing weather information from OpenWeatherMap. See [OpenWeatherMap](https://openweathermap.org/appid).
- `GOOGLE_MAPS_APIKEY`: API key for accessing location data from Google Maps. See [Google Maps](https://developers.google.com/maps/documentation/embed/get-api-key).

Additionally, the following environment variables are used:

- `WEATHER_API_VERSION`: Specifies the version of the OpenWeatherMap API to use. Defaults to 2.5. Note that version 3.0 requires a credit card on file with OpenWeatherMap. For more information, see [One Call API 3.0](https://openweathermap.org/api/one-call-3).


## Notes

- **Database Usage:** Users are stored in a database table named `users`. This table is utilized by various functionalities, such as the `/seen` command. For example, invoking `/seen @username` will provide information on when the specified user was last seen and the message they sent.

- **User Statistics:** The `example/cogs/userstats.py` cog relies on the `GUILD_MEMBERS` privileged intent to track statistics per guild and per user. This allows FlvrBot to gather and analyze data regarding user activity, messages sent, characters typed, and more within each server.

- **Multi-Tenant, Multi-Guild Compatibility:** FlvrBot is designed as a multi-tenant, multi-guild compatible bot. This means that users in different guilds cannot access the statistics or user lists of other guilds. By default each guild's data is accessible only to admin members within that specific server, and the bot owner.

- **Inspired by [BLBot](https://github.com/switch263/BLBot)**
    - FlvrBot is kind of like the cousin of BLBot, a project I've been involved with as a maintainer. I've had my hands in a lot of the cogs there, so FlvrBot naturally shares some similarities and can even use some of the same stuff with slight modification.

