from discord.ext.commands import CommandError


class SnaccmanOnly(CommandError):
	""" Command can only be used by Snaccman. """


class MainServerOnly(CommandError):
	""" Command can only be used in the main server. """


class MissingEmpire(CommandError):
	""" User does not have a empire yet. """


class HasEmpire(CommandError):
	""" User already has an emire. """


class UserOnQuest(CommandError):
	""" User is already on a quest. """


class GlobalCheckFail(CommandError):
	""" Bot global check failed. """
