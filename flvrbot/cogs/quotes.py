import discord
from discord.ext import commands
from flvrbot.db import DBManager
import traceback
import logging

logger = logging.getLogger(__name__)

class QuotesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_manager = DBManager()

    quote_group = discord.SlashCommandGroup("quote", "Manage quotes")

    @quote_group.command(name="add", description="Add a new quote")
    async def add_quote(self, ctx: discord.ApplicationContext, the_quote_to_add: str):
        user_id = ctx.author.id
        guild_id = ctx.guild.id
        self.db_manager.add_quote(user_id, guild_id, the_quote_to_add)
        await ctx.respond(f"Quote added: '{the_quote_to_add}'")

    @quote_group.command(name="list", description="List all quotes in this guild")
    async def list_quotes(self, ctx: discord.ApplicationContext):
        guild_id = ctx.guild.id
        quotes = self.db_manager.get_quotes(guild_id=guild_id)
        if quotes:
            response = "\n".join([
                f"**ID: {q['id']} - Quote:** {q['message']} - Submitter: <@{q['user_id']}> on {q['date_submitted'].strftime('%B %d, %Y at %H:%M')}"
                for q in quotes
            ])
        else:
            response = "No quotes found."
        await ctx.respond(response, ephemeral=True)

    @quote_group.command(name="get", description="Get a quote by ID or text search")
    async def get_quote(self, ctx: discord.ApplicationContext, identifier: str):
        guild_id = ctx.guild.id
        try:
            quote_id = int(identifier)
            quote = self.db_manager.get_quote_by_id(quote_id, guild_id)
            if quote:
                await ctx.respond(
                    f"**Quote:** {quote['message']}\n**submitted by** <@{quote['user_id']}> on {quote['date_submitted'].strftime('%B %d, %Y at %H:%M')}"
                )
            else:
                await ctx.respond("Quote not found.", ephemeral=True)
        except ValueError:
            quotes = self.db_manager.search_quotes_by_text(identifier, guild_id)
            if quotes:
                response = "\n".join([
                    f"**ID: {q['id']} - Quote:** {q['message']}\n**submitted by** <@{q['user_id']}> on {q['date_submitted'].strftime('%B %d, %Y at %H:%M')}"
                    for q in quotes
                ])
                await ctx.respond(response)
            else:
                await ctx.respond("No quotes matching your search were found.", ephemeral=True)

    @quote_group.command(name="delete", description="Delete a quote by ID")
    @commands.has_permissions(administrator=True)
    async def delete_quote(self, ctx: discord.ApplicationContext, id: int):
        guild_id = ctx.guild.id
        result = self.db_manager.delete_quote(id, guild_id)
        if result:
            await ctx.respond("Quote deleted successfully.", ephemeral=True)
        else:
            await ctx.respond("Failed to delete quote or quote not found.", ephemeral=True)

def setup(bot):
    bot.add_cog(QuotesCog(bot))

