import discord

from discord.ext import commands


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
