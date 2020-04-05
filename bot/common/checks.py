

from discord.ext import commands

from bot.common import utils


def channel_has_tag(ctx=None, tag=None):
	""" Can be used as a decorator or a simple function call. Specify <ctx> if function else will return a check """

	def predicate(ctx):
		channels = utils.get_tagged_channels(ctx.bot.svr_cache, ctx.guild, tag)

		if ctx.channel.id not in channels:
			raise commands.CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel")
		return True

	return commands.check(predicate) if ctx is None else predicate(ctx)


def author_has_tagged_role(ctx=None, tag=None):
	""" Can be used as a decorator or a simple function call. Specify <ctx> if function else will return a check """

	def predicate(ctx):
		role = utils.get_tagged_role(ctx.bot.svr_cache, ctx.guild, tag)

		if role not in ctx.author.roles:
			raise commands.CommandError(f"**{ctx.author.display_name}** you need the **{role.name}** role.")
		return True

	return commands.check(predicate) if ctx is None else predicate(ctx)


def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise commands.CommandError(f"**{ctx.author.display_name}**, you do not have access to this command")

	return True
