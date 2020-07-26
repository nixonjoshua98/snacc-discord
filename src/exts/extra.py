

from discord.ext import commands


class Extra(commands.Cog):
	@commands.Cog.listener("on_message")
	async def on_message(self, message):
		pass


def setup(bot):
	bot.add_cog(Extra())
