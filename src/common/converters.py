import discord

import datetime as dt

from discord.ext import commands

from src.common.models import EmpireM


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
	ATTACK_COOLDOWN = 3 #* 3_600

	async def convert(self, ctx, argument):
		user = await super().convert(ctx, argument)

		row = await ctx.bot.pool.fetchrow(EmpireM.SELECT_ROW, user.id)

		time_since_attack = (dt.datetime.utcnow() - row['last_attack']).total_seconds()

		if row is None:
			raise commands.CommandError(f"Target does not have an empire.")

		elif time_since_attack < self.ATTACK_COOLDOWN:
			delta = dt.timedelta(seconds=int(self.ATTACK_COOLDOWN - time_since_attack))

			raise commands.CommandError(f"Target is still recovering from another attack. Try again in `{delta}`")

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
		from src.exts.empire.units import ALL

		try:
			val = int(argument)

		except ValueError:
			unit = discord.utils.get(ALL, db_col=argument.lower())

			if unit is None:
				raise commands.UserInputError(f"A unit with the name `{argument}` could not be found.")

		else:
			unit = discord.utils.get(ALL, id=val)

			if unit is None:
				raise commands.UserInputError(f"A unit with the ID `{val}` could not be found.")

		return unit
