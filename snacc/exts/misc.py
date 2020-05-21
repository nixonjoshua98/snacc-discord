import os

from discord.ext import commands


class Miscellaneous(commands.Cog):

	@commands.command(name="lines")
	async def lines(self, ctx):
		""" Count the number of lines within the bot. """

		lines = 0

		for root, dirs, files in os.walk("./snacc/"):
			for f in files:
				if f.endswith(".py"):
					path = os.path.join(root, f)

					with open(path, "r") as fh:
						for line in fh.read().splitlines():
							if line:
								lines += 1

		await ctx.send(f"I am made up of **{lines:,}** lines of code.")

	@commands.command(name="source")
	async def send_github(self, ctx):
		""" Bot source code. """

		await ctx.send(":gear: https://github.com/nixonjoshua98/discord-snacc-bot")


def setup(bot):
	bot.add_cog(Miscellaneous())
