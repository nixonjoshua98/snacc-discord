import discord

from discord.ext import commands

from bot.common import errors


class CoinSide(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		if argument not in ["tails", "heads"]:
			raise errors.InvalidCoinSide()

		return argument


class RoleTag(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		if argument not in ("entry", "member"):
			raise errors.InvalidRoleTag(tags=("entry", "member"))

		return argument


class DiscordUser(commands.MemberConverter):
	"""
	Converter to ensure that the user is present in the server, not the author or a bot

	@commands.command(...)
	async def my_command(self, ctx, user: NotAuthorOrBotServer()):
		...
	"""

	def __init__(self, *, author_ok: bool = False):
		super(DiscordUser, self).__init__()

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
			raise commands.CommandError(f"User `{argument}` could not be found.")

		if not self.author_ok and member.id == ctx.author.id:
			raise commands.CommandError("You cannot target yourself.")

		elif member.bot:
			raise commands.CommandError("Bot accounts cannot be targeted.")

		return member


class Range(commands.Converter):
	def __init__(self, min_: int, max_: int):
		"""
		:param min_: Minimum value allowed (inclusive)
		:param max_: Maximum value allowed (inclusive)
		"""

		self.min = min_
		self.max = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		"""
		:param ctx: The context which the command was called from
		:param argument: The value which is being checked and converted
		:return int: Converted value between x and y
		"""

		try:
			val = int(argument)

			# Value out of range
			if val > self.max or val < self.min:
				raise commands.UserInputError(f"Argument should be within **{self.min:,} - {self.max:,}**")

		except ValueError:
			raise commands.UserInputError(f"You attempted to use an invalid argument.")

		return val
