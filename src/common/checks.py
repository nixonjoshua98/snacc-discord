

import discord
from discord.ext import commands
from src.common import data_reader

from discord.ext.commands import CommandError
from src.common.errors import MinimumCoinError

from src.common.constants import MEMBER_ROLE_ID, GAME_CHANNELS, RANK_CHANNELS


async def has_member_role(ctx):
	member_role = discord.utils.get(ctx.guild.roles, id=MEMBER_ROLE_ID)

	if member_role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{member_role.name}** role.")

	return True


async def in_game_room(ctx):
	if ctx.channel.id not in GAME_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def in_rank_room(ctx):
	if ctx.channel.id not in RANK_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


def id_exists_in_file(file):
	async def predicate(ctx):
		data = data_reader.read_json(file)

		if data.get(str(ctx.author.id), None) is None:
			raise CommandError(f"**{ctx.author.display_name}** I found no stats for you.")

		return True

	return commands.check(predicate)


def has_minimum_coins(file, amount):
	async def predicate(ctx):
		data = data_reader.read_json(file)

		if data.get(str(ctx.author.id), 0) < amount:
			raise MinimumCoinError(f"**{ctx.author.display_name}** you do you not enough coins to do that :frowning:")

		return True

	return commands.check(predicate)