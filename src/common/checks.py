import discord


def author_is_server_owner(ctx): return ctx.author.id == ctx.guild.owner.id


async def has_role(ctx, *, name: str = None, key: str = None):
	role = None

	if name is not None:
		role = discord.utils.get(ctx.guild.roles, name=name)

	elif key is not None:
		svr = await ctx.bot.get_server(ctx.guild)

		role = ctx.guild.get_role(svr[key])

	return role is not None and role in ctx.author.roles


async def server_has_member_role(ctx):
	config = await ctx.bot.get_server(ctx.guild)

	role = ctx.guild.get_role(config["member_role"])

	return role is not None
