

import discord
from discord.ext import commands
from discord.ext.commands import CommandError
from src.common import constants
from src.common import data_reader


async def has_member_role(ctx):
	member_role = discord.utils.get(ctx.guild.roles, id=constants.MEMBER_ROLE_ID)

	if member_role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}**, you need the **{member_role.name}** role.")

	return member_role in ctx.author.roles


async def in_bot_channel(ctx):
	if ctx.channel.id not in constants.BOT_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**, Commands are disabled in this channel.")

	return ctx.channel.id in constants.BOT_CHANNELS


def id_exists_in_file(file):
	async def predicate(ctx):
		data = data_reader.read_json(file)

		stats = data.get(str(ctx.author.id), None)

		if stats is None:
			raise CommandError(f"**{ctx.author.display_name}**, I found no stats for you.")

		return True

	return commands.check(predicate)
