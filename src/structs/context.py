
from discord.ext import commands


class CustomContext(commands.Context):
	empire_data = dict()
	bank_data = dict()

	population_ = dict()
	upgrades_ = dict()
	bank_ = dict()
