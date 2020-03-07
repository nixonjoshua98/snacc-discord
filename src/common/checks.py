

import discord
from discord.ext import commands
from discord.ext.commands import CommandError

from src.common import FileReader
from src.common.errors import (MinimumCoinError, WrongChannelError)
from src.common.constants import MEMBER_ROLE_ID, GAME_CHANNELS, RANK_CHANNELS, BOT_CHANNELS


async def has_member_role(ctx):
	member_role = discord.utils.get(ctx.guild.roles, id=MEMBER_ROLE_ID)

	if member_role not in ctx.author.roles:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{member_role.name}** role.")

	return True


async def in_any_bot_channel(ctx):
	if ctx.channel.id not in BOT_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def in_game_room(ctx):
	if ctx.channel.id not in GAME_CHANNELS:
		raise WrongChannelError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def in_rank_room(ctx):
	if ctx.channel.id not in RANK_CHANNELS:
		raise WrongChannelError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


def has_minimum_coins(file, amount):
	async def predicate(ctx):
		with FileReader(file) as f:
			data = f.get(str(ctx.author.id), default_val={})

		if data.get("coins", 0) < amount:
			raise MinimumCoinError(f"**{ctx.author.display_name}** you do you not enough coins to do that :frowning:")

		return True

	return commands.check(predicate)