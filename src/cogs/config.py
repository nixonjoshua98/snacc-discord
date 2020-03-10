import discord

from discord.ext import commands

from src.common import checks
from src.common import FileReader
from src.common import myjson

class Config(commands.Cog, name="config"):
	def __init__(self, bot):
		self.bot = bot

		myjson.download_file("server_settings.json")

	async def cog_check(self, ctx: commands.Context):
		return await checks.is_server_owner(ctx)

	@commands.group(name="config", help="Server Owner Stuff")
	async def config(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			await ctx.send("Mhm")

	@config.command(name="setgame", help="Register the channel as a game channel")
	async def add_game_channel(self, ctx: commands.Context):
		with FileReader("server_settings.json") as f:
			server_data = f.get(ctx.guild.id, {})

			server_data["game_channels"] = list(set(server_data.get("game_channels", []) + [ctx.channel.id]))

			f.set(ctx.guild.id, server_data)

			await ctx.send(f"**{ctx.channel.name}** has been registered as a game channel :smile:")

	@config.command(name="setabo", help="Register the channel as an ABO channel")
	async def add_abo_channel(self, ctx: commands.Context):
		with FileReader("server_settings.json") as f:
			server_data = f.get(ctx.guild.id, {})

			server_data["abo_channels"] = list(set(server_data.get("abo_channels", []) + [ctx.channel.id]))

			f.set(ctx.guild.id, server_data)

			await ctx.send(f"**{ctx.channel.name}** has been registered as an ABO channel :smile:")

	@config.command(name="prefix", help="Set the server prefix")
	async def set_server_prefix(self, ctx: commands.Context, new_prefix: str):
		with FileReader("server_settings.json") as f:
			data = f.get(str(ctx.guild.id), default_val={})

			data["prefix"] = new_prefix

			f.set(str(ctx.guild.id), data)

			await ctx.send(f"Prefix has been updated to **{new_prefix}**")

	@config.command(name="member", help="Set the member role")
	async def set_member_role(self, ctx: commands.Context, new_role: discord.Role):
		with FileReader("server_settings.json") as f:
			data = f.get(str(ctx.guild.id), default_val={})

			data["member_role"] = new_role.id

			f.set(str(ctx.guild.id), data)

			await ctx.send(f"Member role has been updated to **{new_role.name}**")