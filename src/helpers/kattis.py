from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import DiscordBot

import discord
from discord.interactions import Interaction
from discord.ui import button, Button, TextInput
import requests
from bs4 import BeautifulSoup
import re
import aiohttp



class InvalidKattisURL(Exception):
    "Raised when the user submits an invalid kattis link or invalid link in general"

    def __init__(self) -> None:
        super().__init__(
            "You have an invalid Kattis profile link or an invalid link in general."
        )


class NotLibertyStudent(Exception):
    "Raised when the user is not under Liberty University in Kattis"

    def __init__(self) -> None:
        super().__init__(
            "Your Kattis profile is not under Liberty University. Make sure to set your university to Liberty University on your Kattis profile settings."
        )


class SignUpModal(discord.ui.Modal):
    def __init__(self, bot: DiscordBot) -> None:
        super().__init__(title="Points Gained Leaderboard - Sign Up")
        self.bot = bot

        self.kattis_profile_url = TextInput(
            label="Kattis Profile URL",
            placeholder="https://open.kattis.com/users/colter-radke",
            min_length=31,
        )
        self.add_item(self.kattis_profile_url)

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        embed = discord.Embed(title="Error", color=0x990000)
        embed.description = error.args[0]

        print(error)
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True, thinking=True)
        url = self.kattis_profile_url.value

        if "https://open.kattis.com/users/" not in url:
            raise InvalidKattisURL()

        url_split = url.split("https://open.kattis.com/users/")
        username = url_split[1]
        username.replace("/", "")
        username.replace(":", "")

        user_score = await get_kattis_score(username)

        if user_score is None:
            raise NotLibertyStudent()

        user = {
            "discord_id": str(interaction.user.id),
            "kattis_username": username,
            "original_points": user_score,
            "current_points": user_score,
        }

        # Can throw UserAlreadyExists error
        await self.bot.database.add_user_to_leaderboard(user)

        embed = discord.Embed(
            title="Success",
            description="You have been added to the leaderboard.\n **Note**: The leaderboard will refresh every day at 11:59 pm",
            color=0x0A254E,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


class SignUpButton(discord.ui.View):
    def __init__(self, bot: DiscordBot):
        super().__init__(timeout=None)
        self.bot = bot
        self.sign_up.custom_id = "sign_up_button"

    @button(label="Sign Up", style=discord.ButtonStyle.blurple, emoji="📝")
    async def sign_up(self, interaction: Interaction, button: Button):
        await interaction.response.send_modal(SignUpModal(self.bot))


# returns an Optional[float]
# Where the optional float is the score
async def get_kattis_score(username):
    url = f"https://open.kattis.com/users/{username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            page_content = await response.text()

    soup = BeautifulSoup(page_content, "html.parser")

    # Check if the user is from Liberty University
    error_check = str(soup.findAll("div", class_="image_info"))
    liberty_check = re.search("Liberty University", error_check)
    is_liberty_student = bool(liberty_check)

    if not is_liberty_student:
        return None

    # Get the score
    line = soup.findAll("span", class_="important_number")
    if len(line) < 2:
        return None  # Return None if the score is not found

    score = str(line[1])
    results = re.findall("[0-9.]+", score)

    if results:
        return float(results[0])
    else:
        return None
