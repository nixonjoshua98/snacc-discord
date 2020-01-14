from discord.ext import commands

from darkness.common import data_reader
import darkness.cogs as cogs


class DarknessBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!")

        self._config = data_reader.read_json("bot_config.json")

        self.command_prefix = self._config["prefix"]

        for c in cogs.cog_list:
            self.add_cog(c(self))

    @staticmethod
    async def on_ready():
        print("Bot ready")

    def run(self):
        super().run(self._config["token"])
