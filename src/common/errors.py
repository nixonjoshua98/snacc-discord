from discord.ext.commands import CommandError


class SnaccmanOnly(CommandError):
	""" Command can only be used by Snaccman. """


class MainServerOnly(CommandError):
	""" Command can only be used in the main server. """
