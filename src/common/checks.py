from discord.ext import commands

from src.common.errors import (
	SnaccmanOnly,
	MainServerOnly,
	MissingEmpire,
	HasEmpire,
	SupportServerOnly
)

from src.common import SNACCMAN, DarknessServer, SupportServer

from src.data import Military


def snaccman_only():
	async def predicate(ctx):
		if ctx.author.id != SNACCMAN:
			raise SnaccmanOnly("You do not have access to this command.")

		return ctx.author.id == SNACCMAN

	return commands.check(predicate)


def has_unit(unit, amount):
	async def predicate(ctx):
		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})

		num_units = units.get(unit.key, 0)

		if num_units < amount:
			raise commands.CommandError(f"You need at least **{amount}x {unit.display_name}** to do that")

		return True

	return commands.check(predicate)


def has_power(amount):
	async def predicate(ctx):
		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})

		power = Military.get_total_power(units)

		if power < amount:
			raise commands.CommandError(f"You need at least **{amount}** power to do that")

		return True

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
		if ctx.guild.id != DarknessServer.ID:
			raise MainServerOnly("This command can only be used in the main server.")

		return ctx.guild.id == DarknessServer.ID

	return commands.check(predicate)


def support_server_only():
	async def predicate(ctx):
		if ctx.guild.id != SupportServer.ID:
			raise SupportServerOnly("This command can only be used in the support server.")

		return True

	return commands.check(predicate)
