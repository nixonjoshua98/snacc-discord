import typing
import discord

from discord.ext import commands


class NotAuthorOrBotServer(commands.MemberConverter):
	"""
	Converter to ensure that the user is present in the server, not the author or a bot

	@commands.command(...)
	async def my_command(self, ctx, user: NotAuthorOrBotServer()):
		...
	"""
	async def convert(self, ctx: commands.Context, argument: str) -> discord.Member:
		"""
		:param ctx: Context in which the command was invoked with
		:param argument: The argument which needs to be checked
		:return: Return the member
		:raise UserInputError: Raises if the member is not valid
		"""
		try:
			member = await super().convert(ctx, argument)
		except commands.BadArgument as e:
			raise commands.UserInputError(f"**{e.args[0]}**")

		if member.id == ctx.author.id or member.bot:
			raise commands.UserInputError(f"User **{member.display_name}** cannot be used as an argument")

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


class ValidTag(commands.Converter):
	def __init__(self, allowed_tags: typing.Union[list, tuple]):
		"""
		:param allowed_tags:
		"""
		self._allowed_tags = allowed_tags

	async def convert(self, ctx: commands.Context, argument: str) -> str:
		"""
		:param ctx: Command context
		:param argument: Value to convert
		:return: Return the tag if i is valid
		"""

		# Invalid tag
		if argument not in self._allowed_tags:
			tag_text = ", ".join(self._allowed_tags)

			raise commands.UserInputError(f"**{argument}** is an invalid tag. Valid Tags: **{tag_text}**")

		return argument