import discord

from discord.ext import commands

from src.common.errors import (
	MissingEmpire,
	HasEmpire,
)

from src.common.population import Military


def has_empire():
	async def predicate(ctx):
		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		if empire is None:
			raise MissingEmpire(f"You do not have an empire. You can establish one using `{ctx.prefix}create`")

		return True

	return commands.check(predicate)


def is_admin():
	async def predicate(ctx):
		permissions = ctx.channel.permissions_for(ctx.author)

		has_admin_role = discord.utils.get(ctx.guild.roles, name="Admin")

		if await ctx.bot.is_owner(ctx.author) or permissions.administrator or has_admin_role:
			return True

		raise commands.CommandError("You need to be an Administrator or have the `Admin` role to access this command.")

	return commands.check(predicate)


def no_empire():
	async def predicate(ctx):
		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		if empire is not None:
			raise HasEmpire(f"You already have an established empire. View your empire using `{ctx.prefix}empire`")

		return True

	return commands.check(predicate)


def has_unit(unit, amount):
	async def predicate(ctx):
		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id}) or dict()

		owned = empire.get("units", dict()).get(unit.key, dict()).get("owned", 0)

		if owned < amount:
			raise commands.CommandError(f"You need at least **{amount}x {unit.display_name}** to do that")

		return True

	return commands.check(predicate)


def has_power(amount):
	async def predicate(ctx):
		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id}) or dict()

		power = Military.calc_total_power(empire)

		if power < amount:
			raise commands.CommandError(f"You need at least **{amount}** power to do that")

		return True

	return commands.check(predicate)