from discord.ext import commands


def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise commands.CommandError(f"You do not have access to this command.")

	return True


async def user_is_member(ctx):
	svr = await ctx.bot.get_server(ctx.guild)

	role = ctx.guild.get_role(svr["memberrole"])

	if svr["memberrole"] == 0 or role is None:
		raise commands.CommandError("A server member role needs to be set first.")

	elif role not in ctx.author.roles:
		raise commands.CommandError("User '{esc.user}' could not be found.")

	return True
