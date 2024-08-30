import os
from dotenv import load_dotenv
import discord
import logging
import aiosqlite
import platform
import sys
import json

from discord.ext import commands, tasks
from discord.ext.commands import Context
from helpers import startup, db_manager, kattis

intents = discord.Intents().default()


with open(f"config.json") as file:
    config = json.load(file)


class LoggingFormatter(logging.Formatter):
    # Colors
    black = "\x1b[30m"
    red = "\x1b[31m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    blue = "\x1b[34m"
    gray = "\x1b[38m"
    # Styles
    reset = "\x1b[0m"
    bold = "\x1b[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger("discord_bot")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
# File handler
file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_handler_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file_handler.setFormatter(file_handler_formatter)

# Add the handlers
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=[],
            intents=intents,
            help_command=None,
        )
        """
        This creates custom bot variables so that we can access these variables in cogs more easily.

        For example, The config is available using the following code:
        - self.config # In this class
        - bot.config # In this file
        - self.bot.config # In cogs
        """
        self.logger = logger
        self.database = None
        self.blue = 0x0A254E
        self.red = 0x990000

    @tasks.loop(minutes=2)
    async def update_leaderboard(self) -> None:
        users = await self.database.get_leaderboard_entries()
        
        for user in users:
            kattis_username = user['kattis_username']
            new_score = await kattis.get_kattis_score(kattis_username)
            
            await self.database.insert_score_snapshot(user['discord_id'], new_score)
            
            user['current_points'] = new_score

        await self.database.update_leaderboard_entries(users)

        channel = await bot.fetch_channel(self.config["leaderboard-channel-id"])

        with open("messages.json", "r") as file:
            messages_json = json.load(file)

        leaderboard_message_id = messages_json["leaderboard-message-id"]

        try:
            await channel.fetch_message(leaderboard_message_id)
        except discord.NotFound:
            leaderboard_message_id = None

        leaderboard_message_id = await startup.setup_leaderboard_message(
            self, channel, leaderboard_message_id
        )

        messages_json["leaderboard-message-id"] = leaderboard_message_id

        with open("messages.json", "w") as file:
            json.dump(messages_json, file)

        bot.logger.info("Leaderboard message updated!")

        


    @update_leaderboard.before_loop
    async def before_update_task(self) -> None:
        await self.wait_until_ready()

    async def init_db(self) -> None:
        async with aiosqlite.connect(
            f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
        ) as db:
            with open(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/schema.sql"
            ) as file:
                await db.executescript(file.read())
            await db.commit()

    async def load_cogs(self) -> None:
        """
        The code in this function is executed whenever the bot will start.
        """
        for file in os.listdir(f"{os.path.realpath(os.path.dirname(__file__))}/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    self.logger.info(f"Loaded extension '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    self.logger.error(
                        f"Failed to load extension {extension}\n{exception}"
                    )    

    async def setup_hook(self) -> None:
        """
        This will just be executed when the bot starts the first time.
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        self.update_leaderboard.start()
        await self.init_db()
        self.config = config
        await self.load_cogs()
        self.database = db_manager.DatabaseManager(
            connection=await aiosqlite.connect(
                f"{os.path.realpath(os.path.dirname(__file__))}/database/database.db"
            )
        )

        self.logger.info("Finished setting up the bot!")
    
    async def on_ready(self):
        await self.change_presence(activity=discord.Game("Kattis problems"))
        guild = await self.fetch_guild(self.config['guild-id'])
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

        await startup.startup(self)

load_dotenv()

bot = DiscordBot()
bot.run(os.getenv("TOKEN"))


