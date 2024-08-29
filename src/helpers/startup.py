from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import DiscordBot


import discord
from discord import Guild


import json
from helpers import kattis


async def startup(bot: DiscordBot):
    guild = bot.get_guild(int(bot.config["guild-id"]))
    channel = await bot.fetch_channel(int(bot.config["leaderboard-channel-id"]))

    with open("messages.json", "r") as file:
        messages_json = json.load(file)

    leaderboard_sign_up_message_id = messages_json["leaderboard-sign-up-message-id"]

    message_id = leaderboard_sign_up_message_id

    try:
        await channel.fetch_message(leaderboard_sign_up_message_id)
    except discord.NotFound:
        message_id = None

    # sets the new message id
    message_id = await setup_signup_message(bot, channel, message_id)

    messages_json["leaderboard-sign-up-message-id"] = message_id

    with open("messages.json", "w") as file:
        json.dump(messages_json, file)

    bot.logger.info("Finished startup!")


# If message_id is None then we need to resend the message
# and return the new message_id for it to be updated in the json
async def setup_signup_message(
    bot: DiscordBot, channel: discord.channel.TextChannel, message_id: int | None
) -> int:
    if message_id is None:
        signup_embed = discord.Embed(
            description="## Points gained leaderboard\nSign up to be included in the leaderboard and have a chance to win prizes!",
            color=0x0A254E,
        )

        message = await channel.send(embed=signup_embed, view=kattis.SignUpButton(bot))
        return message.id
    else:
        bot.add_view(view=kattis.SignUpButton(bot), message_id=message_id)
        return message_id
