import discord
from discord.ext import commands
from discord.ext.commands import UserInputError, BadArgument


class NotAuthorOrBotServer(commands.MemberConverter):
	async def convert(self, ctx: commands.Context, argument: str) -> discord.Member:
		try:
			member = await super().convert(ctx, argument)
		except BadArgument:
			raise UserInputError(f":x: **Member '{argument}' was not found in this server**")

		if member.id == ctx.author.id or member.bot:
			raise UserInputError(f":x: **{ctx.author.display_name}, "
								 f"'{member.display_name}' is either a bot account or your own account**")

		return member


class IntegerAboveZero(commands.Converter):
	async def convert(self, ctx: commands.Context, argument: str) -> int:
		try:
			val = int(argument)

			if val <= 0:
				raise commands.UserInputError(f"**{ctx.author.display_name}, '{argument}' should be > 0**")

		except ValueError:
			raise commands.UserInputError(f"**{ctx.author.display_name}, '{argument}' is not an integer**")

		return val


class IntegerRange(commands.Converter):
	def __init__(self, min_: int, max_: int):
		self._min = min_
		self._max = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		try:
			val = int(argument)

			if val > self._max or val < self._min:
				raise commands.UserInputError(f"**{ctx.author.display_name}, "
											  f"'{argument}' should be between {self._min:,} and {self._max:,}**")

		except ValueError:
			raise commands.UserInputError(f"**{ctx.author.display_name}, '{argument}' is not an integer**")

		return val


class ValidTag(commands.Converter):
	def __init__(self, valid_tags: tuple):
		self._valid_tags = valid_tags

	async def convert(self, ctx: commands.Context, argument: str) -> str:
		argument = argument.lower()

		if argument not in self._valid_tags:
			raise UserInputError(f"Invalid tag ({' or '.join([f'**{t}**' for t in self._valid_tags])})")

		return argument