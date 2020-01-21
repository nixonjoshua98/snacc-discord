import asyncio
import threading
import os

from discord.ext import commands

from darkness.common import data_reader
from darkness.common import myjson

import darkness.cogs as cogs


class DarknessBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", case_insensitive=True)

        config = data_reader.read_json("bot_config.json")

        self.command_prefix = config["prefix"]

        self.remove_command("help")

        for c in cogs.cog_list:
            self.add_cog(c(self))

    async def on_ready(self):
        """ Method which is called once the bot has connected to the Discord servers """

        if not os.getenv("DEBUG", False):
            self.loop.create_task(self.backup_loop())

        print("Bot successfully started")

    async def on_command_error(self, ctx, esc):
        print(esc)

    @staticmethod
    async def backup_loop():
        while True:
            await asyncio.sleep(60 * 30)

            threading.Thread(target=myjson.upload_all).start()

            print("Backing up")

    def run(self):
        # Attempts to start the discord bot

        config = data_reader.read_json("bot_config.json")

        super().run(config["token"])