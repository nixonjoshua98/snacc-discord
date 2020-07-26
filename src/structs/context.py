
from discord.ext import commands


class CustomContext(commands.Context):
	empire_data = dict()  # atk_pow, def_pow
