import discord

from discord.ext import commands

from bot.common import (
	checks,
)

from bot.common.queries import ServersSQL


class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.DEFAULT_ROW = [self.bot.default_prefix, 0]

	async def cog_check(self, ctx: commands.Context):
		return await self.bot.is_owner(ctx.author) or checks.author_is_server_owner(ctx)

	async def cog_before_invoke(self, ctx: commands.Context):
		ctx.server_config = await self.get_server(ctx.guild)

	async def get_server(self, guild):
		""" Return the server configuration or add a new entry and return the default configuration. """
		async with self.bot.pool.acquire() as con:
			async with con.transaction():
				svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

				if svr is None:
					await con.execute(ServersSQL.INSERT_SERVER, guild.id, *self.DEFAULT_ROW)

					svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

		return svr

	@commands.command(name="prefix", usage="<prefix>")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the prefix for this server. """

		await ctx.bot.pool.execute(ServersSQL.UPDATE_PREFIX, ctx.guild.id, prefix)
		await self.bot.update_prefixes(ctx.message)
		await ctx.send(f"Prefix has been updated to **{prefix}**")

	@commands.command(name="setentryrole", usage="<role=0>")
	async def set_entry_role(self, ctx: commands.Context, role: discord.Role = 0):
		"""
Set the role which is given to every user who joins this server.
**Remove** the role by not using any parameters
		"""

		if role == 0:
			await ctx.bot.pool.execute(ServersSQL.UPDATE_ENTRY_ROLE, ctx.guild.id, role)#
			return await ctx.send("Entry role has been removed")

		if role > ctx.guild.me.top_role:
			return await ctx.send(f"I cannot use the role **{role.name}**. The role is higher than me")

		await ctx.bot.pool.execute(ServersSQL.UPDATE_ENTRY_ROLE, ctx.guild.id, role.id)
		await ctx.send(f"Entry role has been set to **{role.name}**")


def setup(bot):
	bot.add_cog(Settings(bot))
