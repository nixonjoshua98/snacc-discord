import discord

import datetime as dt

from discord.ext import commands

from src.common.models import EmpireM, PopulationM

from src.common.empireunits import ALL_UNITS, MilitaryGroup
from src.common.empirequests import EmpireQuests


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

	async def convert(self, ctx, argument):
		user = await super().convert(ctx, argument)

		row = await EmpireM.fetchrow(ctx.bot.pool, user.id, insert=False)

		if row is None:
			raise commands.CommandError(f"Target does not have an empire.")

		time_since_attack = (dt.datetime.utcnow() - row['last_attack']).total_seconds()

		# Target is in cooldown period
		if time_since_attack < self.ATTACK_COOLDOWN:
			delta = dt.timedelta(seconds=int(self.ATTACK_COOLDOWN - time_since_attack))

			raise commands.CommandError(f"Target is still recovering from a previous attack. Try again in `{delta}`")

		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(author_population)

		if author_power < 15:
			raise commands.CommandError("You need at least **15** power to do that.")

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


class EmpireQuest(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"A quest with the ID `{argument}` could not be found.")

		else:
			quest = EmpireQuests.get(id=val)

			if quest is None:
				raise commands.UserInputError(f"A quest with the ID `{val}` could not be found.")

		return quest
