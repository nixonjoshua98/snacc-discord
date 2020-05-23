import discord

from discord.ext import commands


class UserMember(commands.MemberConverter):
	""" Ensures that the member argument has the member role for the server. """

	async def convert(self, ctx, argument) -> discord.Member:
		try:
			member = await super().convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError(f"User '{argument}' could not be found")

		svr = await ctx.bot.get_server(ctx.guild)

		if member.bot:
			raise commands.CommandError("Bot accounts cannot be targeted.")

		elif svr.get("member_role", None) is None:
			raise commands.CommandError("A server member role needs to be set.")

		elif discord.utils.get(member.roles, id=svr["member_role"]) is None:
			raise commands.CommandError(f"User '{member.display_name}' does not have the member role.")

		return member


class NormalUser(commands.MemberConverter):
	async def convert(self, ctx, argument) -> discord.Member:
		try:
			member = await super().convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError(f"User '{argument}' could not be found")

		if member.bot:
			raise commands.CommandError("Bot accounts cannot be targeted.")

		elif member.guild_permissions.administrator:
			raise commands.CommandError("Server admins cannot be targeted.")

		elif ctx.author.id == member.id:
			raise commands.CommandError("You cannot target youself.")

		return member


class Range(commands.Converter):
	def __init__(self, min_: int, max_: int):
		self.min_ = min_
		self.max_ = max_

	async def convert(self, ctx: commands.Context, argument: str) -> int:
		try:
			val = int(argument)

			# Value out of range
			if val > self.max_ or val < self.min_:
				raise commands.UserInputError(f"Argument should be within **{self.min_:,} - {self.max_:,}**")

		except ValueError:
			raise commands.UserInputError(f"You attempted to use an invalid argument.")

		return val
