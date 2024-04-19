import discord
import random
from discord.ext import commands
from flvrbot.db import DBManager

class RouletteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chambers = 6
        self.loaded_chamber = None
        self.shot_count = 0
        self.db_manager = DBManager()
        # Define data map
        self.data_map = {
            "win": {"survive": 1, "death": 0},
            "lose": {"survive": 0, "death": 1}
        }

    def load_chamber(self):
        self.loaded_chamber = random.randint(1, self.chambers)

    @commands.command(help="Plays russian roulette. Example: !roulette [status|reload] where status and reload are optional")
    async def roulette(self, ctx, option=None):
        if option == "reload":
            self.load_chamber()
            self.shot_count = 0
            await ctx.send("🔄 Chamber reloaded. 🔫")
        elif option == "status":
            await ctx.send(f"You are on shot number: {self.shot_count}")
        else:
            self.shot_count += 1
            if self.loaded_chamber is None:
                self.load_chamber()
            if self.shot_count == self.loaded_chamber:
                await ctx.send(f"<@{ctx.author.id}> 💥 **BANG** not so lucky. RIP. 💀")
                self.loaded_chamber = None
                self.shot_count = 0
                await self.record_stats(ctx, "lose")
            else:
                await ctx.send(f"<@{ctx.author.id}> 🔫 **CLICK** You got lucky! 💰")
                await self.record_stats(ctx, "win")

    async def record_stats(self, ctx, result):
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        module = "roulette"
        data = self.data_map[result]

        self.db_manager.update_stats(guild_id=guild_id, user_id=user_id, module=module, data=data)

def setup(bot):
    bot.add_cog(RouletteCog(bot))

