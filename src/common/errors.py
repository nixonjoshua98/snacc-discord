from discord.ext.commands import CommandError


class MinimumCoinError(CommandError):
	""" Has less than the minimum amount of coins """


class NoStatsError(CommandError):
	""" Has never set their ABO game stats """
