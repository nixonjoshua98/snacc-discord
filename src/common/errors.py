from discord.ext.commands import CommandError


class SnaccmanOnly(CommandError):
	""" Command can only be used by Snaccman. """


class MainServerOnly(CommandError):
	""" Command can only be used in the main server. """


class SupportServerOnly(CommandError):
	""" Support server only command. """


class MissingEmpire(CommandError):
	""" User does not have a empire yet. """


class HasEmpire(CommandError):
	""" User already has an emire. """


class GlobalCheckFail(CommandError):
	""" Bot global check failed. """


class NSFWChannelOnly(CommandError):
	""" ... """
