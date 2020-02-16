from discord.ext.commands import CommandError


class MinimumCoinError(CommandError):
	""" Has less than the minimum amount of coins """
