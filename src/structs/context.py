
from discord.ext import commands


class CustomContext(commands.Context):
	bank_data = dict()

	upgrades_ = dict()
	bank_ = dict()

	@property
	def pool(self): return self.bot.pool
