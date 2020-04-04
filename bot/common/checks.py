

import discord

from discord.ext.commands import CommandError


async def channel_has_tag(ctx, tag, svr_cache):
	server = svr_cache.get(ctx.guild.id, None)

	if server is None:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	allowed_channels = server.channels.get(tag, []) if server.channels is not None else []

	if ctx.channel.id not in allowed_channels:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def author_has_tagged_role(ctx, tag, svr_cache):
	server = svr_cache.get(ctx.guild.id, None)

	if server is None:
		raise CommandError(f"**Tagged role {tag} is invalid or has not been set**")

	role = server.roles.get(tag, None) if server.roles is not None else None
	role = discord.utils.get(ctx.guild.roles, id=role)

	if role is None:
		raise CommandError(f"**Tagged role '{tag}' is invalid or has not been set**")

	elif role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{role.name}** role.")

	return True


async def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise CommandError(f"**{ctx.author.display_name}, you do not have access to this command**")

	return True