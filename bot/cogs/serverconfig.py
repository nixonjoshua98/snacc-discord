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

	@commands.command(name="tags", help="List all tags")
	async def list_all_tags(self, ctx: commands.Context):
		return await ctx.send("no")

	@commands.command(name="srt", help="Set role tag")
	async def set_tagged_role(self, ctx: commands.Context, tag: converters.ValidTag(RoleTags.ALL), role: discord.Role):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			roles = dict() if data is None else data.roles if data.roles is not None else dict()  # Lol...

			roles[tag] = role.id

			con.cur.execute(ServerConfigSQL.UPDATE_ROLES, (ctx.guild.id, json.dumps(roles)))

		await ctx.send(f"The role **{role.name}** has been given the tag **{tag}**")

	@commands.command(name="rrt", help="Remove role tag")
	async def remove_role_tag(self, ctx: commands.Context, tag: converters.ValidTag(RoleTags.ALL)):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			roles = dict() if data is None else data.roles if data.roles is not None else dict()  # Lol...

			roles.pop(tag, None)

			con.cur.execute(ServerConfigSQL.UPDATE_ROLES, (ctx.guild.id, json.dumps(roles)))

		await ctx.send(f"The role for **{tag.title()}** has been removed")

	@commands.command(name="act", help="Add channel tag")
	async def add_channel_tag(self, ctx: commands.Context, tag: converters.ValidTag(ChannelTags.ALL)):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			channels = dict() if data is None else data.channels if data.channels is not None else dict()

			channels[tag] = list(set(channels.get(tag, []) + [ctx.channel.id]))

			con.cur.execute(ServerConfigSQL.UPDATE_CHANNELS, (ctx.guild.id, json.dumps(channels)))

		await ctx.send(f"{ctx.channel.mention} has been registered as a **{tag}** channel")

	@commands.command(name="rct", help="Remove channel tag")
	async def remove_channel_tag(self, ctx: commands.Context, tag: converters.ValidTag(ChannelTags.ALL)):
		with DBConnection() as con:
			data = self.bot.svr_cache.get(ctx.guild.id, None)

			channels = dict() if data is None else data.channels if data.channels is not None else dict()

			tagged = list(set(channels.get(tag, [])))

			if ctx.channel.id in tagged:
				tagged.remove(ctx.channel.id)

			channels[tag] = tagged

			con.cur.execute(ServerConfigSQL.UPDATE_CHANNELS, (ctx.guild.id, json.dumps(channels)))

		await ctx.send(f"{ctx.channel.mention} has been unregistered as a **{tag}** channel")

	@commands.command(name="pre", usage="<prefix>")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		with DBConnection() as con:
			con.cur.execute(ServerConfigSQL.UPDATE_PREFIX, (ctx.guild.id, prefix))

		await ctx.send(f"Prefix has been updated to **{prefix}**")


def setup(bot):
	bot.add_cog(ServerConfig(bot))
