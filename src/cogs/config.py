import discord

from discord.ext import commands

from src.common import checks
from src.common import FileReader
from src.common import converters

from src.common.constants import ALL_CHANNEL_TAGS, ALL_ROLE_TAGS


class Config(commands.Cog, name="owner"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx: commands.Context):
		return await self.bot.is_owner(ctx.author) or checks.is_server_owner(ctx)

	@commands.group(name="config", help="Server Configuration")
	async def config(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			return await ctx.send_help(ctx.command)

	@config.command(name="channel", help="Register current channel")
	async def set_channel(self, ctx: commands.Context, tag: converters.ValidTag(ALL_CHANNEL_TAGS)):
		with FileReader("server_settings.json") as server_settings:
			channels = server_settings.get_inner_key((str(ctx.guild.id)), "channels", {})

			channels[tag] = channels.get(tag, []) + [ctx.channel.id]
			channels[tag] = list(set(channels[tag]))

			server_settings.set_inner_key((str(ctx.guild.id)), "channels", channels)

		await ctx.send(f"{ctx.channel.mention} has been registered as an **{tag}** channel")

	@config.command(name="role", help="Register a role")
	async def set_role(self, ctx: commands.Context, tag: converters.ValidTag(ALL_ROLE_TAGS), role: discord.Role):
		with FileReader("server_settings.json") as server_settings:
			roles = server_settings.get_inner_key((str(ctx.guild.id)), "roles", {})

			roles[tag] = role.id

			server_settings.set_inner_key(str(ctx.guild.id), "roles", roles)

		await ctx.send(f"Member role has been updated to **{role.name}**")

	@config.command(name="prefix", help="Set the server prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		with FileReader("server_settings.json") as server_settings:
			server_settings.set_inner_key(str(ctx.guild.id), "prefix", prefix)

		await ctx.send(f"Prefix has been updated to **{prefix}**")
