from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import DiscordBot


import discord
from discord import Guild


import json
from helpers import kattis


async def startup(bot: DiscordBot):
    guild = bot.get_guild(bot.config["guild-id"])
    channel = await bot.fetch_channel(bot.config["leaderboard-channel-id"])

    with open("messages.json", "r") as file:
        messages_json = json.load(file)

    leaderboard_sign_up_message_id = messages_json["leaderboard-sign-up-message-id"]
    # leaderboard_message_id = messages_json["leaderboard-message-id"]

    # try:
    #     await channel.fetch_message(leaderboard_message_id)
    # except discord.NotFound:
    #     leaderboard_message_id = None

    # leaderboard_message_id = await setup_leaderboard_message(
    #     bot, channel, leaderboard_message_id
    # )
    # bot.logger.info("Leaderboard message setup!")

    # messages_json["leaderboard-message-id"] = leaderboard_message_id

    try:
        await channel.fetch_message(leaderboard_sign_up_message_id)
    except discord.NotFound:
        leaderboard_sign_up_message_id = None

    # sets the new message id
    leaderboard_sign_up_message_id = await setup_signup_message(
        bot, channel, leaderboard_sign_up_message_id
    )
    bot.logger.info("Leaderboard sign up message setup!")

    messages_json["leaderboard-sign-up-message-id"] = leaderboard_sign_up_message_id

    with open("messages.json", "r") as file:
        race_condition_json = json.load(file)

    messages_json['leaderboard-message-id'] = race_condition_json['leaderboard-message-id']
    
    with open("messages.json", "w") as file:
        json.dump(messages_json, file)

    bot.logger.info("Finished startup!")


async def setup_leaderboard_message(
    bot: DiscordBot, channel: discord.channel.TextChannel, message_id: int | None
) -> int:
    embed = discord.Embed()
    embed.title = "Kattis Points Gained Leaderboard"
    embed.color = 0x0A254E
    names = []
    points = []
    users = await bot.database.get_leaderboard_entries()

    for user in users:
        names.append(f"<@{user['discord_id']}>")
        points.append(str(round(user["current_points"] - user["original_points"], 1)))

    embed.add_field(name="Name", value="\n".join(names), inline=True)
    embed.add_field(name="Points Gained", value="\n".join(points), inline=True)

    if message_id is None:
        message = await channel.send(embed=embed)
        return message.id
    else:
        message = await channel.fetch_message(message_id)
        await message.edit(embed=embed)
        return message.id


# If message_id is None then we need to resend the message
# and return the new message_id for it to be updated in the json
async def setup_signup_message(
    bot: DiscordBot, channel: discord.channel.TextChannel, message_id: int | None
) -> int:
    if message_id is None:
        signup_embed = discord.Embed(
            description="## Leaderboard Sign Up\nSign up to be included in the leaderboard and have a chance to win prizes!",
            color=0x0A254E,
        )

        message = await channel.send(embed=signup_embed, view=kattis.SignUpButton(bot))
        return message.id
    else:
        bot.add_view(view=kattis.SignUpButton(bot), message_id=message_id)
        return message_id
