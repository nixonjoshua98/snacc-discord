

from discord.ext import commands

from src.common.emoji import Emoji


class Extra(commands.Cog):
	@commands.Cog.listener("on_message")
	async def on_message(self, message):
		pass


def setup(bot):
	bot.add_cog(Extra())
