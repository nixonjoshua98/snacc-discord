from discord.ext.commands import CommandError

class MinimumCoinError(CommandError):
	""" Has less than the minimum amount of coins """

class AutoBattlesStatsError(CommandError):
	""" Has never set their ABO game stats """

class RoleError(CommandError):
	""" User doesn't have the required role """

class WrongChannelError(CommandError):
	""" Command invoked in wrong channel """

class ServerOwnerError(CommandError):
	""" Permission error """

class InvalidTarget(CommandError):
	""" Invalid User """

class SnaccmanError(CommandError):
	""" You are not me """