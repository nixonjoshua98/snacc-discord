
from discord.ext import commands


class Conquest(commands.Cog):
	""" Commands related to the Conquest mode. """

	def __init__(self, bot):
		self.bot = bot


def setup(bot):
	bot.add_cog(Conquest(bot))
