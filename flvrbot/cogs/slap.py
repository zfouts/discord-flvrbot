import discord
import random
import logging
from discord.ext import commands
from flvrbot.db import DBManager

logger = logging.getLogger(__name__)

class SlapCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_users = ["kev2tall"]
        self.db_manager = DBManager()

    def select_article(self, word):
        return "an" if word[0] in 'aeiou' else "a"

    def get_random_slap_item(self):
        slap_items = [
            "trout", "salmon", "goldfish", "carp", "bluegill", "catfish", "bass", "mackerel", "herring", "sardine",
            "pufferfish", "clownfish", "tuna", "swordfish", "halibut", "sturgeon", "anchovy", "snapper", "grouper",
            "flounder", "mahi mahi", "barracuda", "shark", "whale shark", "piranha", "sunfish", "koi", "betta", "perch",
            "tilapia", "gar", "mudfish", "skate", "ray", "blobfish", "anglerfish", "goby", "cichlid", "walleye",
            "sculpin", "roach", "bream", "char", "chub", "dace", "pike", "smelt", "tarpon", "barramundi", "bowfin",
            "buffalo fish", "burbot", "drum", "eel", "flathead", "ide", "loach", "minnow", "mooneye", "moray",
            "mullet", "needlefish", "oscar", "peacock bass", "pollock", "pompano", "rudd", "sauger", "scad",
            "shad", "sole", "sprat", "sucker", "surfperch", "tench", "triggerfish", "tripletail", "wahoo",
            "wrasse", "yellowtail", "zander", "lionfish", "monkfish", "goosefish", "rockfish", "turbot", "lingcod",
            "marlin", "garfish", "flying fish", "coelacanth", "paddlefish", "lamprey", "hagfish", "lungfish", "gurnard",
            "parrotfish", "boxfish", "cowfish", "remora", "ribbonfish", "seahorse", "pipefish", "leafy seadragon",
            "knifefish", "electric eel", "hammerhead shark", "manta ray", "spiny dogfish", "porcupinefish", "cuttlefish",
            "squid", "octopus", "viperfish", "fangtooth", "grenadier", "haddock", "icefish", "john dory", "emperor",
            "queen angelfish", "clown triggerfish", "firefish", "rabbitfish", "batfish", "surgeonfish", "tang",
            "butterflyfish", "mandarinfish", "dragonet", "scorpionfish", "stonefish", "frogfish"
        ]
        
        slap_descriptors = [
            "stinky", "smelly", "oily", "tasty", "slimy", "wet", "giant", "tiny", "colorful", "exotic",
            "spiky", "fluffy", "sleek", "frozen", "slippery", "dried", "fresh", "salty", "sweet", "bitter",
            "smoked", "grilled", "pickled", "steamed", "raw", "crunchy", "mushy", "soggy", "tender", "tough",
            "juicy", "zesty", "fizzy", "glittery", "shiny", "dull", "bright", "dark", "light", "heavy",
            "airy", "smooth", "rough", "prickly", "soft", "hard", "thick", "thin", "dense", "delicate",
            "fragrant", "pungent", "aromatic", "perfumed", "odorless", "scented", "acidic", "creamy", "crispy", "flaky",
            "silky", "waxy", "greasy", "fiery", "icy", "spicy", "chilly", "hot", "cold", "cool",
            "gloopy", "gooey", "chewy", "lumpy", "sparkly", "glowing", "vibrant", "pale", "vivid", "muted"
        ]

        fish = random.choice(slap_items)
        descriptor = random.choice(slap_descriptors)
        article = self.select_article(fish if fish[0] not in 'aeiou' else descriptor)
        return f"{article} {descriptor} {fish}"

    async def slap_target(self, ctx, slapper, target):
        slap_message = f"{slapper.mention} slaps {target.mention} with {self.get_random_slap_item()}!"
        await ctx.send(slap_message)

    def get_valid_target(self, ctx):
        channel_members = [member for member in ctx.channel.members if member.display_name.lower() not in self.ignored_users]
        return random.choice(channel_members)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Slap module has been loaded")

    @commands.command(name='slap', help='Slap someone in the channel. If no one is mentioned, a random person is slapped.')
    async def slap(self, ctx, target: discord.Member = None):
        slapper = ctx.author

        if target == self.bot.user:
            await ctx.send(f"You think you can slap me {slapper.mention}? I don't think so. How about I slap you {slapper.mention}!\n_{self.bot.user.mention} slaps {slapper.mention} with {self.get_random_slap_item()}_!")
            return

        if target == slapper:
            await ctx.send(f"Ha! Quit slapping yourself around {slapper.mention}")
            return

        if target is None:
            target = self.get_valid_target(ctx)

        if target.display_name.lower() in self.ignored_users:
            target = slapper

        await self.slap_target(ctx, slapper, target)

        logger.info(f"{slapper.display_name} slapped {target.display_name}")

        guild_id = ctx.guild.id
        module = "slap"
        stats_updates = {
            ctx.author.id: {"attack": 1, "victim": 0},
            target.id: {"attack": 0, "victim": 1}
        }

        for user_id, data in stats_updates.items():
            self.db_manager.update_stats(guild_id=guild_id, user_id=user_id, module=module, data=data)

def setup(bot):
    bot.add_cog(SlapCog(bot))
