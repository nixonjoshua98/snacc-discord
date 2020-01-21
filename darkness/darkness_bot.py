import os

from discord.ext import commands

import darkness.cogs as cogs


class DarknessBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="?", case_insensitive=True)

        if not os.getenv("DEBUG", False):
            self.command_prefix = "!"

        print("Prefix: " + self.command_prefix)

        self.remove_command("help")

        for c in cogs.cog_list:
            self.add_cog(c(self))

    @staticmethod
    async def on_ready():
        print("Bot successfully started")

    async def on_command_error(self, ctx, esc):
        print(esc)

    def run(self):
        super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")