import discord


def author_is_server_owner(ctx): return ctx.author.id == ctx.guild.owner.id


def author_is_admin(ctx): return ctx.author.guild_permissions.administrator


def message_from_guild(ctx, id_): return ctx.guild.id == id_


async def has_role(ctx, *, name: str = None, key: str = None):
	role = None

	if name is not None:
		role = discord.utils.get(ctx.guild.roles, name=name)

	elif key is not None:
		svr = await ctx.bot.get_server(ctx.guild)

		role = ctx.guild.get_role(svr[key])

	return role is not None and role in ctx.author.roles
