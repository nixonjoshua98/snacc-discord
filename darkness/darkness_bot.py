import discord
from discord.ext import commands

from darkness.common import data_reader
import darkness.cogs as cogs


class DarknessBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="?")

        self._config = data_reader.read_json("bot_config.json")

        self.command_prefix = self._config["prefix"]

        for c in cogs.cog_list:
            self.add_cog(c(self))

    async def on_ready(self):
        """ Method which is called once the bot has connected to the Discord servers """

        self.remove_command("help")

        print("Bot successfully started")

    async def help(self, ctx):
        embed = discord.Embed(
            colour=discord.Colour.orange()
        )

        embed.set_author(name="Help Section")

        embed.add_field(name="help", value="Shows this message", inline=False)

        embed.set_footer(text=self.user.display_name)

        await ctx.send(embed=embed)

    async def on_command_error(self, ctx, excep):
        msg = ctx.message.content

        if msg.startswith(f"{self.command_prefix}help"):
            await self.help(ctx)

    def run(self):
        """
        Attempts to start the discord bot

        :exception RunTimeError: Throws when the bot fails to run
        """
        print("Bot attempting to start")
        super().run(self._config["token"])
