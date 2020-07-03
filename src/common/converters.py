import discord

from discord.ext import commands


class DiscordMember(commands.MemberConverter):
	def __init__(self, *, allow_bots: bool, allow_admins: bool, allow_author: bool, members_only: bool):
		super(DiscordMember, self).__init__()

		self.allow_bots = allow_bots
		self.allow_admins = allow_admins
		self.allow_author = allow_author

		self.members_only = members_only

	async def convert(self, ctx, argument) -> discord.Member:
		try:
			member = await super().convert(ctx, argument)

		except commands.BadArgument:
			raise commands.CommandError(f"User '{argument}' could not be found")

		if not self.allow_bots and member.bot:
			raise commands.CommandError("Bot users are not allowed to be used here.")

		elif not self.allow_admins and member.guild_permissions.administrator:
			raise commands.CommandError("Admin users are not allowed to be used here.")

		elif not self.allow_author and ctx.author.id == member.id:
			raise commands.CommandError("You cannot target yourself here.")

		elif self.members_only:
			svr = await ctx.bot.get_server(ctx.guild)

			role = discord.utils.get(member.roles, id=svr["member_role"])

			if role is None:
				raise commands.CommandError(f"User does not have the member role.")

			elif svr.get("member_role") is None:
				raise commands.CommandError("A server member role needs to be set.")

		return member


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


class MemberUser(DiscordMember):
	def __init__(self):
		super(MemberUser, self).__init__(allow_bots=False, allow_author=True, allow_admins=True, members_only=True)


class NormalUser(DiscordMember):
	def __init__(self):
		super(NormalUser, self).__init__(allow_bots=False, allow_author=False, allow_admins=True, members_only=False)


class CoinSide(commands.Converter):
	async def convert(self, ctx, argument):
		argument = argument.lower()

		if argument not in ["tails", "heads"]:
			raise commands.CommandError("That is an invalid coin side.")

		return argument


class PythonCode(commands.Converter):
	async def convert(self, ctx, argument):
		if argument.startswith("```py") and argument.endswith("```"):
			return argument[5:-3]

		raise commands.CommandError("Python code should be wrapped as a Python code block.")