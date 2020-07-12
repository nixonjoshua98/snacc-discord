import discord

from discord.ext import commands

from src.common.errors import (
	SnaccmanOnly,
	MainServerOnly
)

from src.common import SNACCMAN, MainServer


def snaccman_only():
	async def predicate(ctx):
		if ctx.author.id != SNACCMAN:
			raise SnaccmanOnly("This command can only be used by Snaccman.")

		return ctx.author.id == SNACCMAN

	return commands.check(predicate)


def main_server_only():
	async def predicate(ctx):
		if ctx.guild.id != MainServer.ID:
			raise MainServerOnly("This command can only be used in the main server.")

		return ctx.guild.id == MainServer.ID

	return commands.check(predicate)


async def user_has_role(ctx, *, name: str = None, key: str = None):
	role = None

	if name is not None:
		role = discord.utils.get(ctx.guild.roles, name=name)

	elif key is not None:
		svr = await ctx.bot.get_server(ctx.guild)

		role = ctx.guild.get_role(svr[key])

	return role is not None and role in ctx.author.roles


async def server_has_member_role(ctx):
	config = await ctx.bot.get_server(ctx.guild)

	role = ctx.guild.get_role(config["member_role"])

	return role is not None
