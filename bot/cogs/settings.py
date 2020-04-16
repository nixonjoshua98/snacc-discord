import discord
import json

from discord.ext import commands

from bot.common import (
	checks,
)

from bot.common.queries import ServersSQL

from bot.common import (
	DBConnection,
	ServerConfigSQL
)


class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		# Prefix |
		self.default_row = [self.bot.default_prefix]

	async def cog_check(self, ctx: commands.Context):
		return await self.bot.is_owner(ctx.author) or checks.author_is_server_owner(ctx)

	async def cog_after_invoke(self, ctx: commands.Context):
		await self.bot.update_prefixes(ctx.message)

	async def cog_before_invoke(self, ctx: commands.Context):
		await self.bot.pool.execute(ServersSQL.INSERT_SERVER, *(ctx.guild.id, *self.default_row))

	@commands.command(name="prefix", usage="<prefix>")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the prefix for this server. Bot can always be mentioned. """
		await ctx.bot.pool.execute(ServersSQL.UPDATE_PREFIX, ctx.guild.id, prefix)

		with DBConnection() as con:
			con.cur.execute(ServerConfigSQL.UPDATE_PREFIX, (ctx.guild.id, prefix))

		await ctx.send(f"Prefix has been updated to **{prefix}**")


def setup(bot):
	bot.add_cog(Settings(bot))
