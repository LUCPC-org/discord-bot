import discord
from discord.interactions import Interaction
from discord.ui import button, Button
import requests
from bs4 import BeautifulSoup
import re


class SignUpButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.sign_up.custom_id = "sign_up_button"

    @button(label="Sign Up", style=discord.ButtonStyle.blurple, emoji="📝")
    async def sign_up(self, interaction: Interaction, button: Button):
        await interaction.response.send_message("hi", ephemeral=True)


# returns a tuple of an Optional[float]
# Where the optional float is the score
def get_kattis_score(username):
    url = f"https://open.kattis.com/users/{username}"
    page_to_scrape = requests.get(url)
    soup = BeautifulSoup(page_to_scrape.text, "html.parser")

    # Check if the user is from Liberty University
    error_check = str(soup.findAll("div", class_="image_info"))
    liberty_check = re.search("Liberty University", error_check)
    is_liberty_student = bool(liberty_check)

    if not is_liberty_student:
        return None

    # Get the score
    line = soup.findAll("span", class_="important_number")
    if len(line) < 2:
        return None # Return None if the score is not found

    score = str(line[1])
    results = re.findall("[0-9.]+", score)

    if results:
        return float(results[0])
    else:
        return None