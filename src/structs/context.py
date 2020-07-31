
from discord.ext import commands


class CustomContext(commands.Context):
	empire_data = dict()
	bank_data = dict()
	upgrade_data = dict()
