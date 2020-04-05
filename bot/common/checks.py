

from discord.ext.commands import CommandError

from bot.common import utils


def channel_has_tag(ctx, tag):
	channels = utils.get_tagged_channels(ctx.bot.svr_cache, ctx.guild, tag)

	if ctx.channel.id not in channels:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel")

	return True


def author_has_tagged_role(ctx, tag):
	role = utils.get_tagged_role(ctx.bot.svr_cache, ctx.guild, tag)

	if role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{role.name}** role.")

	return True


async def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise CommandError(f"**{ctx.author.display_name}**, you do not have access to this command")

	return True