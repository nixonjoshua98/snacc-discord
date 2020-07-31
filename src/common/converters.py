import discord

import datetime as dt

from discord.ext import commands
from src.common.models import EmpireM, PopulationM

from src.structs.context import CustomContext


class DiscordUser(commands.Converter):
	async def _convert(self, ctx, argument):
		try:
			user = await commands.MemberConverter().convert(ctx, argument)

		except commands.BadArgument:
			try:
				user = await commands.UserConverter().convert(ctx, argument)

			except commands.BadArgument:
				raise commands.CommandError(f"User '{argument}' could not be found")

		return user

	async def convert(self, ctx, argument) -> discord.Member:
		try:
			member = await self._convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError(f"User '{argument}' could not be found")

		if ctx.author.id == member.id:
			raise commands.CommandError("You can not target yourself.")

		elif member.bot:
			raise commands.CommandError("Bot accounts cannot be used.")

		return member


class EmpireTargetUser(DiscordUser):
	ATTACK_COOLDOWN = 1.5 * 3_600

	async def convert(self, ctx: CustomContext, argument):
		from src.exts.empire.units import MilitaryGroup

		user = await super().convert(ctx, argument)

		row = await ctx.bot.pool.fetchrow(EmpireM.SELECT_ROW, user.id)

		if row is None:
			raise commands.CommandError(f"Target does not have an empire.")

		time_since_attack = (dt.datetime.utcnow() - row['last_attack']).total_seconds()

		# Target is in cooldown period
		if time_since_attack < self.ATTACK_COOLDOWN:
			delta = dt.timedelta(seconds=int(self.ATTACK_COOLDOWN - time_since_attack))

			raise commands.CommandError(f"Target is still recovering from a previous attack. Try again in `{delta}`")

		# Populations of both the attacker and defender
		attacker_pop = await ctx.bot.pool.fetchrow(PopulationM.SELECT_ROW, ctx.author.id)
		defender_pop = await ctx.bot.pool.fetchrow(PopulationM.SELECT_ROW, user.id)

		atk_pow = MilitaryGroup.get_total_power(attacker_pop)
		def_pow = MilitaryGroup.get_total_power(defender_pop)

		if atk_pow < 25:
			raise commands.CommandError("You need at least **25** power to do that.")

		elif def_pow <= (atk_pow // 2):
			raise commands.CommandError("You are too strong for your target.")

		# Custom Context data
		ctx.empire_data = {"atk_pow": atk_pow, "def_pow": def_pow}

		return user


class Range(commands.Converter):
	def __init__(self, min_: int, max_: int):
		self.min_ = min_
		self.max_ = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		try:
			val = int(argument)

			if val > self.max_ or val < self.min_:
				raise commands.UserInputError(f"Argument should be within **{self.min_:,} - {self.max_:,}**")

		except ValueError:
			raise commands.UserInputError(f"You attempted to use an invalid argument.")

		return val


class CoinSide(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		if argument not in ["tails", "heads"]:
			raise commands.CommandError(f"`{argument}` is not a valid coin side.")

		return argument


class BotModule(commands.Converter):
	async def convert(self, ctx, argument):
		module = ctx.bot.get_cog(argument.strip().title())

		if module is None:
			raise commands.CommandError(f"`{argument}` is not a bot module.")

		elif not module.get_commands():
			raise commands.CommandError(f"The module `{module.qualified_name}` has no commands.")

		elif not getattr(module, "__blacklistable__", True):
			raise commands.CommandError(f"The module `{module.qualified_name}` is not blacklistable.")

		return module


class EmpireUnit(commands.Converter):
	async def convert(self, ctx, argument):
		from src.exts.empire.units import ALL_UNITS

		try:
			val = int(argument)

		except ValueError:
			unit = discord.utils.get(ALL_UNITS, db_col=argument.lower())

			if unit is None:
				raise commands.UserInputError(f"A unit with the name `{argument}` could not be found.")

		else:
			unit = discord.utils.get(ALL_UNITS, id=val)

			if unit is None:
				raise commands.UserInputError(f"A unit with the ID `{val}` could not be found.")

		return unit


class EmpireUpgrade(commands.Converter):
	async def convert(self, ctx, argument):
		from src.exts.shop.upgrades import ALL_UPGRADES

		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"An item with the name `{argument}` could not be found.")

		else:
			item = discord.utils.get(ALL_UPGRADES, id=val)

			if item is None:
				raise commands.UserInputError(f"A item with the ID `{val}` could not be found.")

		return item

