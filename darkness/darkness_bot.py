import os

from discord.ext import commands

from darkness.common import myjson

import darkness.cogs as cogs


class DarknessBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", case_insensitive=True)

        myjson.get_json(file="member_stats.json")

        if not os.getenv("DEBUG", False):
            self.command_prefix = "!"

        print("Prefix: " + self.command_prefix)

        self.remove_command("help")

        for c in cogs.cog_list:
            self.add_cog(c(self))

    @staticmethod
    async def on_ready():
        """ Method which is called once the bot has connected to the Discord servers """

        print("Bot successfully started")

    async def on_command_error(self, ctx, esc):
        print(esc)

    def run(self):
        # Attempts to start the discord bot

        super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")