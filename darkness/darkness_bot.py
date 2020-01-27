import os
import asyncio

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

    async def on_ready(self):
        print("Bot successfully started")

        await self.wait_until_ready()

        self.loop.create_task(self.background_loop())

    async def on_command_error(self, ctx, esc):
        await ctx.send(f"*{esc}*")

    async def background_loop(self):
        print("Background loop started")

        while not self.is_closed():
            await asyncio.sleep(15)

        print("Background loop ended")

    def run(self):
        super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")