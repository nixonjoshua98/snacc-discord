
from discord.ext import commands

import datetime as dt

from src.common import UnitValues, BattleValues
from src.common.quests import EmpireQuests
from src.common.upgrades import EmpireUpgrades
from src.common.heroes import ChestHeroes, HeroChests
from src.common.population import Military, Workers


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

	async def convert(self, ctx, argument):
		try:
			member = await self._convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError(f"User '{argument}' could not be found")

		if ctx.author.id == member.id:
			raise commands.CommandError("You can not target yourself.")

		elif member.bot:
			raise commands.CommandError("Bot accounts cannot be used.")

		return member


class EmpireBattleTarget(DiscordUser):

	async def convert(self, ctx, argument):
		user = await super().convert(ctx, argument)

		empire = await ctx.bot.db["empires"].find_one({"_id": user.id})

		if empire is None:
			raise commands.CommandError(f"Target does not have an empire.")

		if (last_battle := empire.get("last_battle")) is None:
			time_since_attack = BattleValues.COOLDOWN

		else:
			time_since_attack = (dt.datetime.utcnow() - last_battle).total_seconds()

		if time_since_attack < BattleValues.COOLDOWN:
			delta = dt.timedelta(seconds=int(BattleValues.COOLDOWN - time_since_attack))

			raise commands.CommandError(f"Target is recovering from a previous battle. Try again in `{delta}`")

		return user


class Range(commands.Converter):
	def __init__(self, min_: int, max_: int = None):
		self.min_ = min_
		self.max_ = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		try:
			val = int(argument)

			if (self.max_ is not None and val > self.max_) or val < self.min_:
				raise commands.UserInputError(f"Argument should be within **{self.min_:,} - {self.max_:,}**")

			elif self.max_ is None and val < self.min_:
				raise commands.UserInputError(f"Argument should be greater than **{self.min_:,}")

		except ValueError:
			raise commands.UserInputError(f"You attempted to use an invalid argument.")

		return val


class AnyoneWithEmpire(DiscordUser):
	async def convert(self, ctx, argument):
		user = await self._convert(ctx, argument)

		empire = await ctx.bot.db["empires"].find_one({"_id": user.id})

		if not empire:
			raise commands.CommandError(f"Target does not have an empire.")

		return user


class EmpireUnit(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			unit = Workers.get(key=argument.lower()) or Military.get(key=argument.lower())

			if unit is None:
				raise commands.UserInputError(f"A unit with the name `{argument}` could not be found.")

		else:
			unit = Workers.get(id=val) or Military.get(id=val)

			if unit is None:
				raise commands.UserInputError(f"A unit with the ID `{val}` could not be found.")

		return unit


class HeroFromChest(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"A hero with the ID `{argument}` could not be found.")

		else:
			hero = ChestHeroes.get(id=val)

			if hero is None:
				raise commands.UserInputError(f"A hero with the ID `{val}` could not be found.")

		return hero


class ValidHeroChest(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"A hero chest with the ID `{argument}` could not be found.")

		else:
			chest = HeroChests.get(id=val)

			if chest is None:
				raise commands.UserInputError(f"A hero chest with the ID `{argument}` could not be found.")

		return chest


class MergeableUnit(EmpireUnit):
	async def convert(self, ctx, argument):
		unit = await super().convert(ctx, argument)

		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		# - Get the data for the entry the user wants to buy
		unit_entry = empire.get("units", dict()).get(unit.key, dict()) if empire is not None else dict()

		owned, level = unit_entry.get("owned", 0), unit_entry.get("level", 0)

		if owned < unit.calc_max_amount(unit_entry):
			raise commands.CommandError(f"Merging requires you reach the owned limit first.")

		elif owned < UnitValues.MERGE_COST:
			raise commands.CommandError(f"Merging consumes **{UnitValues.MERGE_COST}** units")

		if level >= UnitValues.MAX_UNIT_MERGE:
			raise commands.CommandError(f"**{unit.display_name}** has already reached the maximum merge level.")

		return unit


class EmpireUpgrade(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"Upgrade with ID `{argument}` could not be found")

		else:
			item = EmpireUpgrades.get(id=val)

			if item is None:
				raise commands.UserInputError(f"Upgrade with ID `{argument}` could not be found")

		return item


class EmpireQuest(commands.Converter):
	async def convert(self, ctx, argument):
		try:
			val = int(argument)

		except ValueError:
			raise commands.UserInputError(f"Upgrade with ID `{argument}` could not be found")

		else:
			item = EmpireQuests.get(id=val)

			if item is None:
				raise commands.UserInputError(f"Quest with ID `{argument}` could not be found.")

		return item


class CoinSide(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		if argument not in ["tails", "heads"]:
			raise commands.CommandError(f"`{argument}` is not a valid coin side.")

		return argument


class ServerAssignedRole(commands.RoleConverter):
	async def convert(self, ctx, argument):
		try:
			role = await super().convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError("Role not recognised. Remove a role by not specifying a role.")

		if role > ctx.guild.me.top_role:
			raise commands.CommandError("I cannot use that role. It is higher than me in the hierachy.")

		return role
