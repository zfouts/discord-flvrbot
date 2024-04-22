# cogs/rekt.py
import discord
from discord.ext import commands
from flvrbot.db import DBManager
import random
import logging


class RektCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.db_manager = DBManager()
        self.rekt_list = [
            '12 Years a Rekt', '2001: A Rekt Odyssey', 'A Game of Rekt', 'Batrekt Begins', 'Braverekt', 'Call of Rekt: Modern Reking 2',
            'Catcher in the Rekt', 'Cash4Rekt.com', 'Christopher Rektellston', 'Citizen Rekt', 'Finding Rekt', 'Fiddler on the Rekt',
            'Forrekt Gump', 'Gladirekt', 'Grapes of Rekt', 'Grand Rekt Auto V', 'Great Rektspectations', 'Gravirekt', 'Hachi: A Rekt Tale',
            'Harry Potter: The Half-Rekt Prince', 'I am Fire, I am Rekt', 'Left 4 Rekt', 'Legend Of Zelda: Ocarina of Rekt', 'Lord of the Rekts: The Reking of the King',
            'Oedipus rekt', 'Painting The Roses Rekt', 'Paper Scissors Rekt', 'Parks and Rekt', 'Pokemon: Fire Rekt', 'Professor Rekt',
            'Rekt', 'Rekt Box 360', 'Rekt It Ralph', 'Rekt TO REKT ass to ass', 'Rekt and Roll', 'Rekt markes the spot', 'Rekt-22',
            'RektCraft', 'RektE', 'Rektflix', 'Rektal Exam', 'Requiem for a Rekt', 'REKT-E', 'REKT TO REKT ass to ass', 'Shrekt',
            'Ship Rekt', 'Singin\' In The Rekt', 'Spirekted Away', 'Star Trekt', 'Star Wars: Episode VI - Return of the Rekt', 'Terminator 2: Rektment Day',
            'The Arekters', 'The Good, the Bad, and The Rekt', 'The Green Rekt', 'The Hunt for Rekt October', 'The Rekt Files', 'The Rekt Knight',
            'The Rekt Knight Rises', 'The Rekt Side Story', 'The Rekt Ultimatum', 'The Rektfather', 'The Shawshank Rektemption', 'The Silence of the Rekts',
            'There Will Be Rekt', 'Tyrannosaurus Rekt'
        ]

        self.rekt_templates = [
            "{user} just got {title}!",
            "{user}, how does it feel to be {title}?"
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Rekt module has been loaded")

    @commands.slash_command(name="rekt", description="Rekt a member")
    async def rekt(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Option(discord.Member, description="Select a member", required=True) # type: ignore
        ):
    
        title = random.choice(self.rekt_list)
        template = random.choice(self.rekt_templates)
        message = template.format(user=member.mention, title=title)
        await ctx.respond(message)

        guild_id = ctx.guild.id
        module = "rekt"
        stats_updates = {
            ctx.author.id: {"attack": 1, "victim": 0},
            member.id: {"attack": 0, "victim": 1}
        }

        for user_id, data in stats_updates.items():
            self.db_manager.update_stats(guild_id=guild_id, user_id=user_id, module=module, data=data)


def setup(bot):
    bot.add_cog(RektCog(bot))

