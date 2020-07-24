import discord
from discord.ext import commands

from src.common.models import ServersM

from src.structs.textpage import TextPage


class Settings(commands.Cog):
	def cog_check(self, ctx):
		if not ctx.author.guild_permissions.administrator:
			raise commands.MissingPermissions("You do not have access to this command.")

		return True

	async def cog_before_invoke(self, ctx: commands.Context):
		""" Ensure that we have an entry for the guild in the database. """

		_ = await ctx.bot.get_server_config(ctx.guild)

	async def cog_after_invoke(self, ctx):
		await ctx.bot.update_server_cache(ctx.message.guild)

	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" [Admin] Set the prefix for this server. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, prefix=prefix)

		await ctx.send(f"Prefix has been updated to `{prefix}`")

	@commands.command(name="setdefaultrole")
	async def set_default_role(self, ctx: commands.Context, role: discord.Role = None):
		""" [Admin] Set (or remove) the default role which gets added to each member when they join the server. """

		if role is not None and role > ctx.guild.me.top_role:
			return await ctx.send(f"I cannot use the role `{role.name}` since the role is higher than me.")

		await ServersM.set(ctx.bot.pool, ctx.guild.id, default_role=getattr(role, "id", 0))

		if role is None:
			await ctx.send(f"Default role has been removed")

		else:
			await ctx.send(f"The default role has been set to `{role.name}`")

	@commands.command(name="setmemberrole")
	async def set_member_role(self, ctx: commands.Context, role: discord.Role = None):
		""" [Admin] Set (or remove) the member role which can open up server-specific commands for server regulars. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, member_role=getattr(role, "id", 0))

		if role is None:
			await ctx.send(f"The member role has been removed.")

		else:
			await ctx.send(f"The member role has been set to `{role.name}`")

	@commands.command(name="access")
	async def show_channel_permissions(self, ctx):
		""" Display which channels I accept commands from. """

		svr = await ctx.bot.get_server_config(ctx.guild)

		page = TextPage(
			title="Bot Server Access",
			headers=("Channel", "Access"),
			footer="Moderator and Settings commands are excluded from blacklisting."
		)

		for channel in ctx.guild.text_channels:
			access = "Blacklisted" if channel.id in svr["blacklisted_channels"] else "Available"

			page.add_row([channel.name, access])

		await ctx.send(page.get())

	@commands.command(name="bl")
	async def blacklist_channel(self, ctx, *, channel: discord.TextChannel = None):
		""" Blacklist a single channel. """

		channel = ctx.channel if channel is None else channel

		await ServersM.bl_chnl(ctx.bot.pool, ctx.guild.id, channel.id)

		await ctx.send(f"Channel {channel.mention} has been blacklisted.")

	@commands.command(name="blall")
	async def blacklist_all_channels(self, ctx):
		""" Blacklist all currently created channels. """

		async with ctx.bot.pool.acquire():
			for channel in ctx.guild.text_channels:
				await ServersM.bl_chnl(ctx.bot.pool, ctx.guild.id, channel.id)

		await ctx.send(f"All **currently created** text channels have been blacklisted.")

	@commands.command(name="wl")
	async def whitelist_channel(self, ctx, *, channel: discord.TextChannel = None):
		""" Whitelist a single channel. """

		channel = ctx.channel if channel is None else channel

		await ServersM.wl_chnl(ctx.bot.pool, ctx.guild.id, channel.id)

		await ctx.send(f"Channel {channel.mention} is no longer blacklisted.")

	@commands.command(name="wlall")
	async def whitelist_all_channels(self, ctx):
		""" Whitelist all currently created channels. """

		async with ctx.bot.pool.acquire():
			for channel in ctx.guild.text_channels:
				await ServersM.wl_chnl(ctx.bot.pool, ctx.guild.id, channel.id)

		await ctx.send(f"All **currently created** text channels are no longer blacklisted.")


def setup(bot):
	bot.add_cog(Settings())
