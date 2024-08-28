import discord
from discord.interactions import Interaction
from discord.ui import button, Button

class SignUpButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.sign_up.custom_id = 'sign_up_button'

    @button(label="Sign Up", style=discord.ButtonStyle.blurple, emoji='📝')
    async def sign_up(self, interaction : Interaction, button: Button):
        await interaction.response.send_message('hi', ephemeral=True)