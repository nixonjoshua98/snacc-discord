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

		elif discord.utils.get(member.roles, id=svr["memberrole"]) is None:
			raise commands.CommandError(f"User '{member.display_name}' does not have the member role.")

		return member