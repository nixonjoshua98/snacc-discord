import discord
import json

from discord.ext import commands

from bot.common import checks
from bot.common import converters
from bot.common.database import DBConnection

from bot.common import queries

from bot.common.constants import ALL_CHANNEL_TAGS, ALL_ROLE_TAGS


class Config(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx: commands.Context):
		return await self.bot.is_owner(ctx.author) or await checks.author_is_server_owner(ctx)

	async def cog_after_invoke(self, ctx: commands.Context):
		await self.bot.update_cache(ctx.message)

	@commands.group(name="config", help="Server Configuration")
	async def config(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			return await ctx.send_help(ctx.command)

	@config.command(name="channel", help="Register current channel")
	async def set_channel(self, ctx: commands.Context, tag: converters.ValidTag(ALL_CHANNEL_TAGS)):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			channels = data.channels or dict()
			channels[tag] = list(set(channels.get(tag, []) + [ctx.channel.id]))
			dumps = json.dumps(channels)

			con.cur.execute(queries.UPDATE_SVR_CHANNELS_SQL, (ctx.guild.id, dumps))

		await ctx.send(f"{ctx.channel.mention} has been registered as an **{tag}** channel")

	@config.command(name="role", help="Register a role")
	async def set_role(self, ctx: commands.Context, tag: converters.ValidTag(ALL_ROLE_TAGS), role: discord.Role):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			roles = dict() if data is None else data.roles if data.roles is not None else dict()  # Lol...
			roles[tag] = role.id
			dumps = json.dumps(roles)

			con.cur.execute(queries.UPDATE_SVR_ROLES_SQL, (ctx.guild.id, dumps))

		await ctx.send(f"**{tag.title()}** role has been updated to **{role.name}**")

	@config.command(name="prefix", help="Set the server prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		with DBConnection() as con:
			con.cur.execute(queries.UPDATE_PREFIX_SQL, (ctx.guild.id, prefix))

		await ctx.send(f"Prefix has been updated to **{prefix}**")


def setup(bot):
	bot.add_cog(Config(bot))