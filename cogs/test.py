import discord
from discord import app_commands
from discord.ext import commands

class Test(commands.Cog, name="test"):
    @app_commands.command(name="hello-world", description="simple program")
    async def hello_world(self, interaction: discord.Interaction):

        embed = discord.Embed(title="Hello World")
        embed.description = f"hi, {interaction.user.name}"

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Test(bot))