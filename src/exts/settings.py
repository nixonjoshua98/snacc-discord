import discord
from discord.ext import commands

from src.common.queries import ServersSQL


class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_before_invoke(self, ctx: commands.Context):
		""" Ensure that we have an entry for the guild in the database. """

		_ = await self.bot.get_server(ctx.guild)

	async def cog_after_invoke(self, ctx):
		await self.bot.update_server_cache(ctx.message.guild)

	async def get_server_settings(self, guild):
		""" Return the server configuration or add a new entry and return the default configuration """

		async with self.bot.pool.acquire() as con:
			async with con.transaction():
				svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

				if svr is None:
					await con.execute(ServersSQL.INSERT_SERVER, guild.id, "!", 0, 0, False)

					svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

		return svr

	@commands.has_permissions(administrator=True)
	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" [Admin] Set the prefix for this server. """

		await ctx.bot.pool.execute(ServersSQL.UPDATE_PREFIX, ctx.guild.id, prefix)

		await ctx.send(f"Prefix has been updated to `{prefix}`")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setdefaultrole")
	async def set_default_role(self, ctx: commands.Context, role: discord.Role = None):
		""" [Admin] Set (or remove) the default role which gets added to each member when they join the server. """

		if role > ctx.guild.me.top_role:
			return await ctx.send(f"I cannot use the role `{role.name}` since the role is higher than me.")

		await ctx.bot.pool.execute(ServersSQL.UPDATE_DEFAULT_ROLE, ctx.guild.id, 0 if role is None else role.id)

		if role is None:
			await ctx.send(f"Default role has been removed")

		else:
			await ctx.send(f"The default role has been set to `{role.name}`")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setmemberrole")
	async def set_member_role(self, ctx: commands.Context, role: discord.Role = None):
		""" [Admin] Set (or remove) the member role which can open up server-specific commands for server regulars. """

		await ctx.bot.pool.execute(ServersSQL.UPDATE_MEMBER_ROLE, ctx.guild.id, 0 if role is None else role.id)

		if role is None:
			await ctx.send(f"Member role has been removed.")

		else:
			await ctx.send(f"The member role has been set to `{role.name}`")


def setup(bot):
	bot.add_cog(Settings(bot))
