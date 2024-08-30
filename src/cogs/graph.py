import discord
from discord import app_commands
from discord.ext import commands
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime


class Graph(commands.Cog, name="graph"):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="generate-user-graph", description="Generates a graph of the user's points over time")
    async def generate_user_graph(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(thinking=True)
        user_id = str(user.id)
        does_user_exist = await self.bot.database.does_user_exist(user_id)

        if not does_user_exist:
            embed = discord.Embed(title="Error", description="User does not exist in the database", color=self.bot.red)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        user_snapshots = await self.bot.database.get_user_scores_over_time(user_id)

        for snapshot in user_snapshots:
            print(snapshot)


        y_values = [snapshot["score"] for snapshot in user_snapshots]
        x_values = [datetime.strptime(snapshot["date"], "%Y-%m-%d") for snapshot in user_snapshots]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x_values, y_values)
        # Format the x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())

        # Rotate and align the tick labels so they look better
        plt.gcf().autofmt_xdate()

        # Add labels and title
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.set_title(f"{user.name}'s Score Over Time")

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig("graph.png")
        plt.cla()
        plt.clf()
        plt.close('all')
        plt.close(fig)

        file = discord.File("graph.png")
        embed = discord.Embed(title=f"{user.name}'s Score Over Time", color=self.bot.blue)
        embed.set_image(url="attachment://graph.png")

        await interaction.followup.send(embed=embed, file=file, ephemeral=True)        


async def setup(bot):
    await bot.add_cog(Graph(bot))