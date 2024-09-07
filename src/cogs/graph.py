import discord
from discord import app_commands
from discord.ext import commands
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import gc


class Graph(commands.Cog, name="graph"):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="generate-user-graph", description="Generates a graph of the user's points over time")
    async def generate_user_graph(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(thinking=True)
        user_id = str(user.id)
        does_user_exist = await self.bot.database.does_user_exist(user_id)

        if not does_user_exist:
            embed = discord.Embed(title="Error", description=f"User <@{user.id}> does not exist in the database", color=self.bot.red)
            await interaction.followup.send(embed=embed)
            return

        user_snapshots = await self.bot.database.get_user_scores_over_time(user_id)

        y_values = [snapshot["score"] for snapshot in user_snapshots]
        x_values = [datetime.strptime(snapshot["date"], "%Y-%m-%d") for snapshot in user_snapshots]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x_values, y_values)
        # Format the x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))

        # Rotate and align the tick labels so they look better
        plt.gcf().autofmt_xdate()

        # Add labels and title
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.set_title(f"{user.display_name}'s Kattis Score Over Time")

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig("graph.png")
        fig.clf()
        plt.cla()
        plt.clf()
        plt.close('all')
        plt.close(fig)
        del fig
        gc.collect()

        file = discord.File("graph.png")
        embed = discord.Embed(title=f"{user.name}'s Score Over Time", color=self.bot.blue)
        embed.set_image(url="attachment://graph.png")

        await interaction.followup.send(embed=embed, file=file, ephemeral=True)        

    @app_commands.command(name="generate-liberty-graph", description="Generates a graph of Liberty's points over time")
    async def generate_liberty_graph(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        liberty_snapshots = await self.bot.database.get_liberty_scores_over_time()

        y_values_score = [snapshot["score"] for snapshot in liberty_snapshots]
        y_values_rank = [snapshot["rank"] for snapshot in liberty_snapshots]
        x_values = [datetime.strptime(snapshot["date"], "%Y-%m-%d") for snapshot in liberty_snapshots]
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Plot score
        color1 = 'tab:blue'
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Score", color=color1)
        ax1.plot(x_values, y_values_score, color=color1, label="Score")
        ax1.tick_params(axis='y', labelcolor=color1)

        # Create a second y-axis for rank
        ax2 = ax1.twinx()
        color2 = 'tab:orange'
        ax2.set_ylabel("Rank", color=color2)
        ax2.plot(x_values, y_values_rank, color=color2, label="Rank")
        ax2.tick_params(axis='y', labelcolor=color2)
        ax2.yaxis.set_major_locator(ticker.IndexLocator(base=1,offset=0))

        # Format the x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))

        # Rotate and align the tick labels so they look better
        plt.gcf().autofmt_xdate()

        # Add title and legend
        ax1.set_title("Liberty's Kattis Score and Rank Over Time")
        fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)

        # Adjust layout and save
        plt.tight_layout()
        plt.savefig("graph.png")
        fig.clf()
        plt.cla()
        plt.clf()
        plt.close('all')
        plt.close(fig)
        del fig
        gc.collect()

        file = discord.File("graph.png")
        embed = discord.Embed(title="Liberty's Score Over Time", color=self.bot.blue)
        embed.set_image(url="attachment://graph.png")

        await interaction.followup.send(embed=embed, file=file, ephemeral=True)        


async def setup(bot):
    await bot.add_cog(Graph(bot))
