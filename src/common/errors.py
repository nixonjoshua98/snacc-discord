from discord.ext.commands import CommandError


class MinimumCoinError(CommandError):
	""" Has less than the minimum amount of coins """


class AutoBattlesStatsError(CommandError):
	""" Has never set their ABO game stats """


class WrongChannelError(CommandError):
	""" Command invoked in wrong channel """
