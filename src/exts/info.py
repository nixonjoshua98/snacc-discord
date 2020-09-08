import discord

from discord.ext import commands


class Info(commands.Cog):
	__can_disable__ = False

	@commands.command(name="modules")
	async def show_modules(self, ctx):
		""" Show which modules have been disabled or enabled in this server. """

		svr = await ctx.bot.db["servers"].find_one({"_id": ctx.guild.id}) or dict()

		disabled_modules = svr.get("disabled", dict()).get("modules", [])

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

		embed.add_field(name="Enabled Modules", value=" ".join(enabled) or "\u200b", inline=False)
		embed.add_field(name="Disabled Modules", value=" ".join(disabled) or "\u200b", inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="ping")
	async def ping(self, ctx):
		""" Check the bot latency. """

		await ctx.send(f"Pong! {round(ctx.bot.latency * 1000, 3)}ms")

	@commands.command(name="uptime")
	async def show_uptime(self, ctx):
		""" Display the bot uptime """

		embed = ctx.bot.embed(title="Bot Stats")

		embed.add_field(name="Bot", value=f"**Uptime: ** `{ctx.bot.uptime}`")

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Info())
