import discord
from discord.ext import commands
from lenny import lenny
import logging
from datetime import datetime, timedelta
import pytz

logger = logging.getLogger(__name__)

class BasicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = datetime.utcnow()

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Basic commands module has been loaded")

    @commands.slash_command(name="ping", description="Check if the bot is online.")
    async def ping(
        self,
        ctx: discord.ApplicationContext # type: ignore
        ):
        await ctx.respond(f"PONG. Latency is {self.bot.latency:.3f}ms")

    @commands.slash_command(name="joined", help="Displays the join date of a member. Example: !joined @member")
    async def joined(
        self,
        ctx: discord.ApplicationContext,
        member: discord.Option(discord.Member, description="Select a member", required=True) # type: ignore
        ):
        await ctx.respond(f'{member.name} joined in {member.joined_at}')

    @commands.slash_command(name="lenny", description="Generate random lenny face")
    async def lenny(self, ctx: discord.ApplicationContext):
        await ctx.respond(lenny())

    @discord.slash_command(name="info", description="Displays user and guild info. Admin role required.")
    @commands.has_permissions(administrator=True)
    async def info(
        self, 
        ctx: discord.ApplicationContext,
        member: discord.Option(discord.Member, description="Select a member", required=False) ): # type: ignore

        if member is None:
            member = ctx.author

        user = member
        guild = ctx.guild
        roles = [role.name for role in user.roles if role.name != "@everyone"]
        join_date = user.joined_at.replace(tzinfo=pytz.UTC)

        # Calculate duration since joining
        now = datetime.now(pytz.UTC)
        delta = now - join_date
        years = delta.days // 365
        days = delta.days % 365
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        info_str = (
            f"User: {user.name}\n"
            f"Roles: {', '.join(roles)}\n"
            f"Guild ID: {guild.id}\n"
            f"User ID: {user.id}\n"
            f"Channel ID: {ctx.channel.id}\n"
            f"Join Date: {join_date.strftime('%Y-%m-%d %H:%M:%S')} "
            f"({years} years {days} days {hours} hours {minutes} minutes {seconds} seconds)"
        )
        await ctx.respond(info_str)

    @commands.slash_command(name="uptime", description="Responds how long the bot has been online for.")
    @commands.has_permissions(administrator=True)
    async def uptime(self, ctx):
        uptime = datetime.utcnow() - self.bot.start_time
        human_readable = str(uptime).split(".")[0]
        await ctx.respond(f"I have been online for {human_readable}")

def setup(bot):
    bot.add_cog(BasicCog(bot))

