import discord

import datetime as dt

from discord.ext import commands

from src.common.models import EmpireM, PopulationM, UserUpgradesM

from src.data import EmpireQuests, EmpireUpgrades, MilitaryGroup, MoneyGroup


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
	ATTACK_COOLDOWN = 2.0 * 3_600

	async def convert(self, ctx, argument):
		user = await super().convert(ctx, argument)

		row = await EmpireM.fetchrow(ctx.bot.pool, user.id, insert=False)

		if row is None:
			raise commands.CommandError(f"Target does not have an empire.")

		time_since_attack = (dt.datetime.utcnow() - row['last_attack']).total_seconds()

		# - Target is in cooldown period
		if time_since_attack < self.ATTACK_COOLDOWN:
			delta = dt.timedelta(seconds=int(self.ATTACK_COOLDOWN - time_since_attack))

			raise commands.CommandError(f"Target is still recovering from a previous attack. Try again in `{delta}`")

		population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)
		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(population, upgrades)

		if author_power < 25:
			raise commands.CommandError("You need at least **25** power to do that.")

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


class EmpireUnit(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"Units should be referenced by their IDs")

		else:
			unit = MoneyGroup.get(id=val) or MilitaryGroup.get(id=val)

			if unit is None:
				raise commands.UserInputError(f"A unit with the ID `{val}` could not be found.")

		return unit


class EmpireUpgrade(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"Upgrades should be referenced by their IDs")

		else:
			upgrade = EmpireUpgrades.get(id=val)

			if upgrade is None:
				raise commands.UserInputError(f"Upgrade with ID `{val}` could not be found.")

		return upgrade


class EmpireQuest(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"Quests should be referenced by their IDs")

		else:
			quest = EmpireQuests.get(id=val)

			if quest is None:
				raise commands.UserInputError(f"A quest with the ID `{val}` could not be found.")

		return quest


class ServerAssignedRole(commands.RoleConverter):
	async def convert(self, ctx, argument):
		try:
			role = await super().convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError("Role not recognised. Remove a role by not specifying a role.")

		if role > ctx.guild.me.top_role:
			return await ctx.send(f"I cannot use that role. It is higher than me in the hierachy.")

		return role


class TimePeriod(commands.Converter):
	async def convert(self, ctx, argument):
		seconds = self.get_seconds(argument)

		if seconds < 5 or seconds > 604_800:
			raise commands.UserInputError("Time period must be between `5s` and `7d`")

		return dt.timedelta(seconds=seconds)

	def get_seconds(self, argument):
		lookup = {"s": lambda n: n, "m": lambda n: n * 60, "h": lambda n: 3600 * n, "d": lambda n: (3600 * n) * 24}

		ls = argument.split()

		seconds = 0

		if len(ls) == 1 and ls[0].isdigit():
			seconds = int(ls[0])

		else:
			for i, ele in enumerate(ls):
				if len(ele) > 1 and ele[:-1].isdigit():
					num = int(ele[:-1])

					func = lookup.get(ele[-1].lower())

					if func is None:
						continue

					seconds += func(num)

		return seconds

