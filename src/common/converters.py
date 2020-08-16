import discord

import datetime as dt

from discord.ext import commands

from src.common import EmpireConstants

from src.data import EmpireQuests, EmpireUpgrades, Military, Workers


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

		empire = await ctx.bot.mongo.find_one("empires", {"_id": user.id})

		if not empire:
			raise commands.CommandError(f"Target does not have an empire.")

		if empire.get("last_attack") is None:
			time_since_attack = self.ATTACK_COOLDOWN

		else:
			time_since_attack = (dt.datetime.utcnow() - empire['last_attack']).total_seconds()

		# - Target is in cooldown period
		if time_since_attack < self.ATTACK_COOLDOWN:
			delta = dt.timedelta(seconds=int(self.ATTACK_COOLDOWN - time_since_attack))

			raise commands.CommandError(f"Target is still recovering from a previous attack. Try again in `{delta}`")

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
			unit = Workers.get(id=val) or Military.get(id=val)

			if unit is None:
				raise commands.UserInputError(f"A unit with the ID `{val}` could not be found.")

		return unit


class MergeableUnit(EmpireUnit):
	async def convert(self, ctx, argument):
		unit = await super().convert(ctx, argument)

		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		levels = await ctx.bot.mongo.find_one("levels", {"_id": ctx.author.id})

		if units.get(unit.key, 0) < unit.calc_max_amount(levels.get(unit.key, 0)):
			raise commands.CommandError(f"Merging requires you reach the owned limit first.")

		elif units.get(unit.key, 0) < EmpireConstants.MERGE_COST:
			raise commands.CommandError(f"Merging consumes **{EmpireConstants.MERGE_COST}** units")

		levels = await ctx.bot.mongo.find_one("levels", {"_id": ctx.author.id})

		if levels.get(unit.key, 0) >= EmpireConstants.MAX_UNIT_MERGE:
			raise commands.CommandError(f"**{unit.display_name}** has already reached the maximum merge level.")

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

