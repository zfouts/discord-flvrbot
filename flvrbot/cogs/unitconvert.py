import discord
from discord.ext import commands
import pint

class UnitConverterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ureg = pint.UnitRegistry()

    @discord.slash_command(name="convert", description="Converts units from one to another.")
    async def convert(
        self, 
        ctx: discord.ApplicationContext,
        value: discord.Option(float, description="Enter the numerical value you want to convert"), # type: ignore
        unit_from: discord.Option(str, description="Enter the unit you are converting from"), # type: ignore
        unit_to: discord.Option(str, description="Enter the unit you are converting to") # type: ignore
    ):
        try:
            # Check if this is a temperature conversion and handle accordingly
            if unit_from in ["f", "fahrenheit", "F", "degree_Fahrenheit"] and unit_to in ["c", "celsius", "C", "degree_Celsius"]:
                temp = pint.Quantity(value, self.ureg.degree_Fahrenheit)
                converted_temp = temp.to(self.ureg.degree_Celsius)
                friendly_from = "Fahrenheit"
                friendly_to = "Celsius"
            elif unit_from in ["c", "celsius", "C", "degree_Celsius"] and unit_to in ["f", "fahrenheit", "F", "degree_Fahrenheit"]:
                temp = pint.Quantity(value, self.ureg.degree_Celsius)
                converted_temp = temp.to(self.ureg.degree_Fahrenheit)
                friendly_from = "Celsius"
                friendly_to = "Fahrenheit"
            else:
                # Create a quantity object with the source unit
                quantity = pint.Quantity(value, self.ureg(unit_from))
                # Convert to the target unit
                converted_temp = quantity.to(unit_to)
                # Use Pint's units to get the unit names
                friendly_from = str(quantity.units)
                friendly_to = str(converted_temp.units)

            # Send the result back to the Discord channel using respond
            await ctx.respond(f"{value} {friendly_from} is {converted_temp.magnitude:.2f} {friendly_to}")
        except Exception as e:
            # Send an error message if something goes wrong (e.g., invalid units)
            await ctx.respond(str(e))

def setup(bot):
    bot.add_cog(UnitConverterCog(bot))

