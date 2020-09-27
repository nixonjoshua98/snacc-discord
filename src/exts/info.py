import os
import discord

from discord.ext import commands

from src.common import SupportServer


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
					can_run_ = await discord.utils.maybe_coroutine(cog.cog_check, ctx)
				except commands.CommandError:
					return False

				return can_run_

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

		svr = await ctx.bot.db["servers"].find_one({"_id": ctx.guild.id}) or dict()

		whitelisted_channels = svr.get("whitelisted_channels", [])

		embed = ctx.bot.embed(title="Channel Whitelist")

		value = []

		for channel in ctx.guild.text_channels:
			if channel.id in whitelisted_channels:
				perms = channel.permissions_for(ctx.author)

				value.append(channel.mention if perms.read_messages else "`[hidden]`")

		embed.add_field(name="Whitelisted", value=" | ".join(value) or "All channels whitelisted")

		await ctx.send(embed=embed)

	@commands.command(name="links", aliases=["invite", "support", "vote"])
	async def links(self, ctx):
		""" Show the invite links for the bot. """

		embed = ctx.bot.embed(title="Bot Links")

		bot_invite = "https://discord.com/oauth2/authorize?client_id=666616515436478473&scope=bot&permissions=387136"

		bot_vote = "https://top.gg/bot/666616515436478473"

		vote_text = f"You can vote for me [here]({bot_vote})"

		embed.add_field(name="Invite", value=f"Click [here]({bot_invite}) to add me to your server", inline=False)
		embed.add_field(name="Vote (soon rewarded)", value=f"{vote_text}", inline=False)
		embed.add_field(name="Support", value=f"Join my support server [here]({SupportServer.LINK})", inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="stats", aliases=["bot", "ping", "uptime", "lines"])
	async def stats(self, ctx):
		""" Show stats about the bot. """

		embed = ctx.bot.embed(title="Bot Stats")

		lines = 0

		for root, dirs, files in os.walk("./src/"):
			for f in files:
				if not f.endswith(".py"):
					continue

				path = os.path.join(root, f)

				with open(path, "r") as fh:
					lines += len(tuple(line for line in fh.read().splitlines() if line))

		embed.add_field(name="Uptime", value=ctx.bot.uptime)
		embed.add_field(name="Ping", value=f"{round(ctx.bot.latency * 1000, 3)}ms")
		embed.add_field(name="Lines", value=lines)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Info())
