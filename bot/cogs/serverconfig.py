import discord
import json

from discord.ext import commands

from bot.common import (
	checks,
	converters
)

from bot.common import (
	RoleTags,
	ChannelTags,
	DBConnection,
	ServerConfigSQL
)


class ServerConfig(commands.Cog, name="Config"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx: commands.Context):
		return await self.bot.is_owner(ctx.author) or checks.author_is_server_owner(ctx)

	async def cog_after_invoke(self, ctx: commands.Context):
		await self.bot.update_cache(ctx.message)

	@commands.group(name="c", help="Server config")
	async def config(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			return await ctx.send_help(ctx.command)

	@config.command(name="channel")
	async def set_channel(self, ctx: commands.Context, tag: converters.ValidTag(ChannelTags.ALL)):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			channels = data.channels or dict()
			channels[tag] = list(set(channels.get(tag, []) + [ctx.channel.id]))
			dumps = json.dumps(channels)

			con.cur.execute(ServerConfigSQL.UPDATE_CHANNELS, (ctx.guild.id, dumps))

		await ctx.send(f"{ctx.channel.mention} has been registered as an **{tag}** channel")

	@config.command(name="role")
	async def set_role(self, ctx: commands.Context, tag: converters.ValidTag(RoleTags.ALL), role: discord.Role):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			roles = dict() if data is None else data.roles if data.roles is not None else dict()  # Lol...

			roles[tag] = role.id

			con.cur.execute(ServerConfigSQL.UPDATE_ROLES, (ctx.guild.id, json.dumps(roles)))

		await ctx.send(f"**{tag.title()}** role has been updated to **{role.name}**")

	@config.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		with DBConnection() as con:
			con.cur.execute(ServerConfigSQL.UPDATE_PREFIX, (ctx.guild.id, prefix))

		await ctx.send(f"Prefix has been updated to **{prefix}**")


def setup(bot):
	bot.add_cog(ServerConfig(bot))