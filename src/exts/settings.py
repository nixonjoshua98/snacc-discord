import discord
import itertools

from discord.ext import commands

from src.common.models import ServersM
from src.common.converters import BotModule

from src.structs.textpage import TextPage


class Settings(commands.Cog):
	"""
Modules and non-mentioned channels such as `Arena Stats`
will need to be wrapped in speech marks. e.g `!blm "Arena Stats" Empire ...`
"""

	__blacklistable__ = False

	def cog_check(self, ctx):
		if not ctx.author.guild_permissions.administrator:
			raise commands.MissingPermissions(("Administrator",))

		return True

	async def cog_after_invoke(self, ctx):
		await ctx.bot.update_server_cache(ctx.message.guild)

	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server-wide prefix. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, prefix=prefix)

		await ctx.send(f"Prefix has been updated to `{prefix}`")

	@commands.command(name="setdefaultrole")
	async def set_default_role(self, ctx: commands.Context, role: discord.Role = None):
		""" Set (or remove) the default role which gets added to each member when they join the server. """

		if role is not None and role > ctx.guild.me.top_role:
			return await ctx.send(f"I cannot use the role `{role.name}` since the role is higher than me.")

		await ServersM.set(ctx.bot.pool, ctx.guild.id, default_role=getattr(role, "id", 0))

		if role is None:
			await ctx.send(f"Default role has been removed")

		else:
			await ctx.send(f"The default role has been set to `{role.name}`")

	@commands.command(name="setmemberrole")
	async def set_member_role(self, ctx: commands.Context, role: discord.Role = None):
		""" Set (or remove) the member role which can open up server-specific commands for server regulars. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, member_role=getattr(role, "id", 0))

		if role is None:
			await ctx.send(f"The member role has been removed.")

		else:
			await ctx.send(f"The member role has been set to `{role.name}`")

	@commands.command(name="access")
	async def show_channel_access(self, ctx):
		""" Display which channels I accept commands from. """

		svr = await ctx.bot.get_server_config(ctx.guild)

		page = TextPage(
			title="Blacklisted Channels & Modules",
			headers=("Channels", "Modules"),
			footer="Moderator and Settings modules are excluded from blacklisting."
		)

		for chnl, module in itertools.zip_longest(svr["blacklisted_channels"], svr["blacklisted_cogs"], fillvalue=""):
			if chnl:
				chnl = discord.utils.get(ctx.guild.text_channels, id=chnl)
				chnl = f"#{chnl.name}" if chnl is not None else "[DELETED]"

			page.add_row([chnl, module])

		await ctx.author.send(page.get())

		await ctx.send("I have DM'ed you.")

	@commands.command(name="blc")
	async def blacklist_channel(self, ctx, *channels: discord.TextChannel):
		""" Blacklist the current channel or specify a channel. """

		channels = (ctx.channel,) if len(channels) == 0 else channels

		await ServersM.blacklist_channels(ctx.bot.pool, ctx.guild.id, [c.id for c in channels])

		await ctx.send(f"Channels blacklisted: {', '.join((c.mention for c in channels))}")

	@commands.command(name="wlc")
	async def whitelist_channel(self, ctx, *channels: discord.TextChannel):
		""" Whitelist a list of channels. e.g !wlc c1 c2 c3. """

		channels = (ctx.channel,) if len(channels) == 0 else channels

		await ServersM.whitelist_channels(ctx.bot.pool, ctx.guild.id, [c.id for c in channels])

		await ctx.send(f"Channels removed from blacklist: {', '.join((c.mention for c in channels))}")

	@commands.command(name="blm")
	async def blacklist_module(self, ctx, *modules: BotModule()):
		""" Blacklist a list of command modules server-wide """

		modules = list(ctx.cogs.values()) if len(modules) == 0 else modules

		await ServersM.blacklist_modules(ctx.bot.pool, ctx.guild.id, [m.qualified_name for m in modules])

		await ctx.send(f"Modules blacklisted: {', '.join((m.qualified_name for m in modules))}")

	@commands.command(name="wlm")
	async def whitelist_module(self, ctx, *modules: BotModule()):
		""" Whitelist a list of command modules server-wide. e.g !wlm m1 m2 m3. """

		modules = list(ctx.cogs.values()) if len(modules) == 0 else modules

		await ServersM.whitelist_modules(ctx.bot.pool, ctx.guild.id, [m.qualified_name for m in modules])

		await ctx.send(f"Modules removed from server blacklist: {', '.join((m.qualified_name for m in modules))}")


def setup(bot):
	bot.add_cog(Settings())
