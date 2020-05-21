from discord.ext import commands


def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise commands.CommandError(f"You do not have access to this command.")

	return True


async def user_has_member_role(ctx):
	svr = await ctx.bot.get_server(ctx.guild)

	role = ctx.guild.get_role(svr["member_role"])

	if svr["member_role"] == 0 or role is None:
		raise commands.CommandError("A server member role needs to be set.")

	elif role not in ctx.author.roles:
		raise commands.CommandError(f"You need the `{role.name}` role.")

	return True


def from_guild(guild_id):
	async def predicate(ctx):
		return ctx.guild.id == guild_id

	return commands.check(predicate)
