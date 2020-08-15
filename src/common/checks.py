from discord.ext import commands

from src.common.errors import (
	SnaccmanOnly,
	MainServerOnly,
	MissingEmpire,
	HasEmpire,
)

from src.common import SNACCMAN, MainServer


def snaccman_only():
	async def predicate(ctx):
		if ctx.author.id != SNACCMAN:
			raise SnaccmanOnly("You do not have access to this command.")

		return ctx.author.id == SNACCMAN

	return commands.check(predicate)


def has_empire():
	async def predicate(ctx):
		empire = await ctx.bot.mongo.find_one("empires", {"_id": ctx.author.id})

		if not empire:
			raise MissingEmpire(f"You do not have an empire yet. You can establish one using `{ctx.prefix}create`")

		return True

	return commands.check(predicate)


def no_empire():
	async def predicate(ctx):
		empire = await ctx.bot.mongo.find_one("empires", {"_id": ctx.author.id})

		if empire:
			raise HasEmpire(f"You already have an established empire. View your empire using `{ctx.prefix}empire`")

		return True

	return commands.check(predicate)


def main_server_only():
	async def predicate(ctx):
		if ctx.guild.id != MainServer.ID:
			raise MainServerOnly("This command can only be used in the main server.")

		return ctx.guild.id == MainServer.ID

	return commands.check(predicate)