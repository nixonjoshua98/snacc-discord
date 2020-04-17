import discord

from discord.ext import commands


class DiscordUser(commands.UserConverter):
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
			raise commands.CommandNotFound(f"User `{argument}` could not be found.")

		if not self.author_ok and member.id == ctx.author.id:
			raise commands.CommandNotFound("You cannot target youself.")

		elif member.bot:
			raise commands.CommandNotFound("Bot accounts cannot be used here.")

		return member


class IntegerRange(commands.Converter):
	def __init__(self, min_: int, max_: int):
		"""
		:param min_: Minimum value allowed (inclusive)
		:param max_: Maximum value allowed (inclusive)
		"""
		self._min = min_
		self._max = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		"""
		:param ctx: The context which the command was called from
		:param argument: The value which is being checked and converted
		:return int: Converted value between x and y
		"""
		try:
			val = int(argument)

			# Value out of range
			if val > self._max or val < self._min:
				raise commands.UserInputError(f"Argument **{val}** should be within **{self._min:,} - {self._max:,}**")

		except ValueError:
			# Invalid data type
			raise commands.UserInputError(f"Argument **{argument}** is not an integer")

		return val


class Clamp(commands.Converter):
	def __init__(self, min_: int, max_: int):
		self._min = min_
		self._max = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		try:
			val = max(self._min, min(int(argument), self._max))

		except ValueError:
			raise commands.UserInputError(f"You tried to use an invalid paramater.")

		return val