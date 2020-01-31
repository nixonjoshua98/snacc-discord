import discord

from discord.ext.commands import CommandError

from darkness.common.constants import (BOT_CHANNELS, MEMBER_ROLE_NAME)


async def can_use_command(ctx):

	# Ignore DMs
	if ctx.guild is None:
		return False

	member_role = discord.utils.get(ctx.guild.roles, name=MEMBER_ROLE_NAME)

	# Correct channel
	if ctx.channel.id not in BOT_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**. Commands are disabled in this channel")

	# Not owner or not owner (me)
	elif member_role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}**. You must be a member to use this command")

	return True