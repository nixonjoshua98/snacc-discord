

import discord
from discord.ext.commands import CommandError
from src.common import constants


async def has_member_role(ctx):
	member_role = discord.utils.get(ctx.guild.roles, id=constants.MEMBER_ROLE_ID)

	if member_role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}**, you need the **{member_role.name}** role.")

	return member_role in ctx.author.roles


async def message_from_guild(ctx):
	if ctx.guild is None:
		raise CommandError(f"Ignoring DM from **{ctx.author.name}**.")

	return ctx.guild is not None


async def in_bot_channel(ctx):
	if ctx.channel.id not in constants.BOT_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**, Commands are disabled in this channel.")

	return ctx.channel.id in constants.BOT_CHANNELS
