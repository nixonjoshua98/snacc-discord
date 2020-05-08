

from discord.ext import commands

from bot.common import errors


def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise commands.CommandError(f"**{ctx.author.display_name}**, you do not have access to this command")

	return True


async def server_has_member_role(ctx):
	svr = await ctx.bot.get_server(ctx.guild)

	role = ctx.guild.get_role(svr["memberrole"])

	if svr["memberrole"] == 0 or role is None:
		raise errors.MemberRoleNotFound()

	return True
