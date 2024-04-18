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

## Usage

Once the bot is running in your Discord server, you can use the following commands:

- `!top10`: View user activity statistics.
- `!uptime`: View the bot's uptime. (admin role)
- `!seen`: Provide information on when the specified user was last seen and the message they sent. (admin only)
- `!convert`: Converts various units of measurements using [pint](https://pint.readthedocs.io/en/stable/).

## Environment variables

Currently, this bot uses a few variables.

- `DISCORD_TOKEN`: This is the token you receive from Discord. Default: `None`
- `DB_URL`: This is a sqlachemy database url string. Default: `sqlite:////tmp/flvrbot.db`


## Notes

- **Intents Requirement:** FlvrBot currently requires all intents, including privileged intents, to function properly. If your Discord server is large, ensure that Discord allows privileged intents for your bot to access all necessary information.

- **Database Usage:** Users are stored in a database table named `users`. This table is utilized by various functionalities, such as the `!seen` command. For example, invoking `!seen @username` will provide information on when the specified user was last seen and the message they sent.

- **User Statistics:** The `userstats` cog relies on the `GUILD_MEMBERS` privileged intent to track statistics per guild and per user. This allows FlvrBot to gather and analyze data regarding user activity, messages sent, characters typed, and more within each server.

- **Multi-Tenant, Multi-Guild Compatibility:** FlvrBot is designed as a multi-tenant, multi-guild compatible bot. This means that users in different guilds cannot access the statistics or user lists of other guilds. By default each guild's data is accessible only to admin members within that specific server, and the bot owner.

