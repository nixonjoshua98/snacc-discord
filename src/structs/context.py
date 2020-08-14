
from discord.ext import commands


class CustomContext(commands.Context):
	bank_data = dict()

	@property
	def pool(self): return self.bot.pool
