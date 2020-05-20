import discord

from discord.ext import commands


class CoinSide(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		if argument not in ["tails", "heads"]:
			raise commands.CommandError("That is an invalid coin side.")

		return argument


class RoleTag(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		tags = ("entry", "member")

		if argument not in tags:
			raise commands.CommandError(f"Invalid Tag. Tags include: **{', '.join(tags)}**")

		return argument


class DiscordUser(commands.MemberConverter):
	"""  Converter to ensure that the user is present in the server, not the author or a legacy. """

	def __init__(self, *, author_ok: bool = False):
		super().__init__()

		self.author_ok = author_ok

	async def convert(self, ctx: commands.Context, argument: str) -> discord.Member:
		"""
		:param ctx: Context in which the command was invoked with
		:param argument: The argument which needs to be checked
		:return: Return the member
		:raise UserInputError: Raises if the member is not valid
		"""

		try:
			member = await super().convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError(f"User '{argument}' could not be found")

		if not self.author_ok and member.id == ctx.author.id:
			raise commands.CommandError("You cannot target yourself.")

		elif member.bot:
			raise commands.CommandError("Bot accounts cannot be targeted.")

		return member


class Range(commands.Converter):
	def __init__(self, min_: int, max_: int, *, clamp: bool = False):
		"""
		:param min_: Minimum value allowed (inclusive)
		:param max_: Maximum value allowed (inclusive)
		"""

		self.min_ = min_
		self.max_ = max_

		self.clamp = clamp

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		"""
		:param ctx: The context which the command was called from
		:param argument: The value which is being checked and converted
		:return int: Converted value between x and y
		"""

		try:
			val = int(argument)

			# Value out of range
			if val > self.max_ or val < self.min_:
				if not self.clamp:
					raise commands.UserInputError(f"Argument should be within **{self.min_:,} - {self.max_:,}**")

				val = max(min(val, self.max_), self.min_)

		except ValueError:
			raise commands.UserInputError(f"You attempted to use an invalid argument.")

		return val
