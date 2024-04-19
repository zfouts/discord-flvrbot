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

    def has_admin_role(self, user):
        return any(role.name.lower() == "admin" for role in user.roles)

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Basic commands module has been loaded")

    @commands.command(name='ping', aliases=['Ping'], help="Check if the bot is online.")
    async def ping(self, ctx):
        await ctx.send(f"PONG. Latency is {self.bot.latency:.3f}ms")

    @commands.command(help="Displays the join date of a member. Example: !joined @member")
    async def joined(self, ctx, member: discord.Member):
        await ctx.send(f'{member.name} joined in {member.joined_at}')

    @commands.command(help="Sends a lenny face.")
    async def lenny(self, ctx):
        await ctx.send(lenny())

    @commands.command(hidden=True, help="Displays user and guild info. Admin role required.")
    async def info(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author

        if self.has_admin_role(ctx.author):
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
            await ctx.send(info_str)
        else:
            await ctx.send("You need to have the Admin role to use this command.")

    @commands.command(hidden=True, help="Displays how long the bot has been running. Admin role required.")
    async def uptime(self, ctx):
        if self.has_admin_role(ctx.author):
            uptime = datetime.utcnow() - self.bot.start_time
            human_readable = str(uptime).split(".")[0]
            await ctx.send(f"I have been online for {human_readable}")
        else:
            await ctx.send("You need to have the Admin role to use this command.")


def setup(bot):
    bot.add_cog(BasicCog(bot))


