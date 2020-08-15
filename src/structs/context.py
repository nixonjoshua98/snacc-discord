
from discord.ext import commands


class CustomContext(commands.Context):
	@property
	def pool(self): return self.bot.pool
