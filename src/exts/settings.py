import discord

from discord.ext import commands

from src.common import checks

from src.common.errors import CogNotFound


class Settings(commands.Cog):

	__can_disable__ = False
	__override_channel_whitelist__ = True

	async def cog_after_invoke(self, ctx):
		await ctx.bot.update_server_data(ctx.guild)

	@checks.is_admin()
	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server prefix. """

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}, upsert=True)

		await ctx.send(f"Server prefix has been updated to `{prefix}`")

	@checks.is_admin()
	@commands.command(name="togglehelp")
	async def toggle_dm_help(self, ctx):
		""" Toggle whether to DM help to the user or to the server. """

		svr = await ctx.bot.get_server_data(ctx.guild)

		if not svr.get("dm_help", False):
			await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"dm_help": True}}, upsert=True)

			return await ctx.send("Send Help Command: `DM`")

		else:
			await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"dm_help": False}}, upsert=True)

			return await ctx.send("Send Help Command: `Server`")

	@checks.is_admin()
	@commands.command(name="toggle")
	async def toggle_module(self, ctx: commands.Context, *, module):
		""" Toggle a module between enabled and disabled for the server. """

		def get_module():
			for key, inst in ctx.bot.cogs.items():
				if module.lower() in (key.lower(), inst.__class__.__name__.lower()):
					return inst

			return None

		if (module := get_module()) is None:
			raise CogNotFound("Module not found.")

		elif len(module.get_commands()) == 0 or not getattr(module, "__can_disable__", True):
			return await ctx.send("This module cannot be disabled.")

		module_name = module.__class__.__name__

		if await ctx.bot.is_command_enabled(ctx.guild, module):
			query = {"$pull": {"disabled_modules": module_name}}

			await ctx.send(f"Module **{module_name}** has been enabled.")

		else:
			query = {"$push": {"disabled_modules": module_name}}

			await ctx.send(f"Module **{module_name}** has been disabled.")

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, query, upsert=True)

	@checks.is_admin()
	@commands.command(name="togglechannel")
	async def toggle_channel(self, ctx, *, channel: discord.TextChannel):
		""" Whitelist a channel. All channels are whitelisted initially. """

		svr = await ctx.bot.get_server_data(ctx.guild)

		whitelisted_channels = svr.get("whitelisted_channels", [])

		if channel.id in whitelisted_channels:
			query = {"$pull": {"whitelisted_channels": channel.id}}

			await ctx.send(f"Channel {channel.mention} is no longer whitelisted.")

		else:
			query = {"$push": {"whitelisted_channels": channel.id}}

			await ctx.send(f"Channel {channel.mention} is now whitelisted")

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, query, upsert=True)


def setup(bot):
	bot.add_cog(Settings())
