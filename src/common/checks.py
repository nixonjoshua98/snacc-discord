

import discord
import random

from discord.ext import commands
from discord.ext.commands import CommandError

from src.common import FileReader
from src.common.constants import SNACCMAN_ID


def percent_chance_to_run(percentage, fail_message):
	async def predicate(ctx):
		can_run = random.randint(1, 100) <= percentage

		if not can_run:
			raise CommandError(f"**{ctx.author.display_name}** " + fail_message)

		return True

	return commands.check(predicate)


async def is_server_owner(ctx):
	if ctx.author.id not in (ctx.guild.owner.id, SNACCMAN_ID):
		raise CommandError(f"**{ctx.author.display_name}**, you do not have access to this command")

	return True


async def has_member_role(ctx):
	with FileReader("server_settings.json") as f:
		member_role_id = f.get(ctx.guild.id, default_val={}).get("member_role", None)

	member_role = discord.utils.get(ctx.guild.roles, id=member_role_id)

	if member_role is None:
		raise CommandError(f"**{ctx.guild.owner.mention}** member role is invalid or has not been set")

	elif member_role not in ctx.author.roles and ctx.author.id != SNACCMAN_ID:
		raise CommandError(f"**{ctx.author.display_name}** you need the **{member_role.name}** role.")

	return True


async def in_any_bot_channel(ctx):
	with FileReader("server_settings.json") as f:
		abo_channels = f.get(ctx.guild.id, default_val={}).get("abo_channels", [])
		game_channels = f.get(ctx.guild.id, default_val={}).get("game_channels", [])

	channels = abo_channels + game_channels

	if ctx.channel.id not in channels:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def in_game_channel(ctx):
	with FileReader("server_settings.json") as f:
		game_channels = f.get(ctx.guild.id, default_val={}).get("game_channels", [])

	if ctx.channel.id not in game_channels:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


async def in_abo_channel(ctx):
	with FileReader("server_settings.json") as f:
		abo_channels = f.get(ctx.guild.id, default_val={}).get("abo_channels", [])

	if ctx.channel.id not in abo_channels:
		raise CommandError(f"**{ctx.author.display_name}**, this command is disabled in this channel.")

	return True


def has_minimum_coins(file, amount):
	async def predicate(ctx):
		with FileReader(file) as f:
			data = f.get(str(ctx.author.id), default_val={})

		if data.get("coins", 0) < amount:
			raise CommandError(f"**{ctx.author.display_name}** you do you not enough coins to do that :frowning:")

		return True

	return commands.check(predicate)