

from discord.ext.commands import CommandError

from bot.common import utils


async def channel_has_tag(ctx, tag, svr_cache):
	channels = utils.get_tagged_channels(svr_cache, ctx.guild, tag)

	if ctx.channel.id not in channels:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def author_has_tagged_role(ctx, tag, svr_cache):
	role = utils.get_tagged_role(svr_cache, ctx.guild, tag)

	if role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{role.name}** role.")

	return True


async def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise CommandError(f"**{ctx.author.display_name}, you do not have access to this command**")

	return True