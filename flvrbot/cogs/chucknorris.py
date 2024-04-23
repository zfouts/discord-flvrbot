import discord
from discord.ext import commands
import aiohttp  # For asynchronous HTTP requests

class ChuckNorrisFactsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    @discord.slash_command(name='chucknorris', description='Get a random Chuck Norris fact')
    async def chuck_norris_fact(self, ctx: discord.ApplicationContext):
        url = 'https://api.chucknorris.io/jokes/random'
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                chuck_fact = data['value']
                await ctx.respond(chuck_fact)
        except aiohttp.ClientError as e:
            await ctx.respond(f'Failed to fetch Chuck Norris fact: {e}')
        except KeyError:
            await ctx.respond('Failed to parse Chuck Norris fact response.')
        except Exception as e:
            await ctx.respond(f'An error occurred: {e}')

def setup(bot):
    bot.add_cog(ChuckNorrisFactsCog(bot))

