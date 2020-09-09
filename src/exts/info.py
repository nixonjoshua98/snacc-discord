import discord

from discord.ext import commands


class Info(commands.Cog):
	__can_disable__ = False

	@commands.command(name="modules")
	async def show_modules(self, ctx):
		""" Show which modules are enabled in this server. """

		svr = await ctx.bot.db["servers"].find_one({"_id": ctx.guild.id}) or dict()

		disabled_modules = svr.get("disabled_modules", [])

		embed = ctx.bot.embed(title="Server Modules")

		async def can_run(cog):
			if hasattr(cog, "__help_verify_checks__"):
				try:
					await discord.utils.maybe_coroutine(cog.cog_check, ctx)
				except commands.CommandError:
					return False

			return True

		enabled, disabled = [], []

		for name, inst in ctx.bot.cogs.items():
			if len(inst.get_commands()) == 0 or not await can_run(inst):
				continue

			ls = disabled if inst.__class__.__name__ in disabled_modules else enabled

			ls.append(f"`{name}`")

		embed.add_field(name="Enabled Modules", value=" | ".join(enabled) or "\u200b", inline=False)
		embed.add_field(name="Disabled Modules", value=" | ".join(disabled) or "\u200b", inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="channels")
	async def show_channels(self, ctx):
		""" Show the server channel whitelist. """

		svr = await ctx.bot.get_server_data(ctx.guild)

		whitelisted_channels = svr.get("whitelisted_channels", [])

		embed = ctx.bot.embed(title="Channel Whitelist")

		value = []

		for channel in ctx.guild.text_channels:
			if channel.id in whitelisted_channels:
				value.append(channel.mention)

		embed.add_field(name="Whitelisted", value=" | ".join(value) or "All channels whitelisted")

		await ctx.send(embed=embed)

	@commands.command(name="ping")
	async def ping(self, ctx):
		""" View my latency. """

		await ctx.send(f"Pong! {round(ctx.bot.latency * 1000, 3)}ms")

	@commands.command(name="support")
	async def support(self, ctx):
		""" Link to the support server. """

		await ctx.send("https://discord.gg/QExQuvE")

	@commands.command(name="invite")
	async def send_bot_invite(self, ctx):
		""" Invite me to your server! """

		await ctx.send("https://discord.com/oauth2/authorize?client_id=666616515436478473&scope=bot&permissions=387136")

	@commands.command(name="vote")
	async def vote(self, ctx):
		""" Link to the vote site. """

		await ctx.send("https://discord.boats/bot/666616515436478473\nhttps://top-bots.xyz/bot/666616515436478473")

	@commands.command(name="uptime")
	async def show_uptime(self, ctx):
		""" Display how long I have been awake. """

		embed = ctx.bot.embed(title="Bot Stats")

		embed.add_field(name="Bot", value=f"**Uptime: ** `{ctx.bot.uptime}`")

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Info())
