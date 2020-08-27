import discord

from discord.ext import commands

from src.aboapi import API

from src.common import checks

from src.structs import TextPage, Confirm


class ABO(commands.Cog):

	@checks.snaccman_only()
	@commands.command(name="setaboname")
	async def set_abo_name(self, ctx, user: discord.Member, *, name):
		""" Associate a Discord user to a user in ABO. """

		embed = ctx.bot.embed(title="Auto Battles Online", description=f"{user.mention}'s username is `{name}`?")

		if not await Confirm(embed).prompt(ctx):
			return await ctx.send("Operation aborted.")

		await ctx.bot.mongo.set_one("players", {"_id": user.id}, {"abo_name": name})

		await ctx.send(f"Username has been set to `{name}`")

	@commands.group(name="lb", hidden=True, invoke_without_command=True)
	async def leaderboard_group(self, ctx):
		""" ... """

	@leaderboard_group.command(name="guilds")
	async def get_guilds(self, ctx):
		""" Show the top 15 entries on the guild leaderboard. """

		guilds = await API.leaderboard.get_guilds(pos=0, count=15)

		page = TextPage(title="Guilds", headers=["Rank", "Name", "Rating"])

		for guild in guilds:
			row = [f"#{guild.rank:02d}", guild.name, f"{guild.rating:,}"]

			page.add(row)

		await ctx.send(page.get())

	@leaderboard_group.command(name="players")
	async def get_players(self, ctx):
		""" Show the top 15 entries on the player leaderboard. """

		players = await API.leaderboard.get_players(pos=0, count=15)

		page = TextPage(title="Players", headers=["Rank", "Name", "Rating"])

		for player in players:
			row = [f"#{player.rank:02d}", player.name, f"{player.rating:,}"]

			page.add(row)

		await ctx.send(page.get())

	@leaderboard_group.command(name="player")
	async def get_player(self, ctx, *, name):
		""" Show information about a player. """

		player = await API.leaderboard.get_player(name)

		if player is None:
			return await ctx.send(f"I found no player named `{name}`")

		embed = ctx.bot.embed(title=f"{player.name} [Guild: {player.guild if player.guild is not None else 'N/A'}]")

		embed.description = (
			f"Rank: **#{player.rank:02d}**\n"
			f"Level: **{player.level:,}**\n"
			f"Rating: **{player.rating:,}**\n"
		)

		await ctx.send(embed=embed)

	@leaderboard_group.command(name="guild")
	async def get_guild(self, ctx, *, name):
		""" Show information about a guild. """

		guild = await API.leaderboard.get_guild(name)

		if guild is None:
			return await ctx.send(f"I found no guild named `{name}`")

		embed = ctx.bot.embed(title=f"{guild.name} [Leader: {guild.leader}]")

		embed.description = (
			f"Rank: **#{guild.rank:02d}**\n"
			f"Rating: **{guild.rating:,}**\n"
			f"Member Count: **{guild.size:,}**"
		)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(ABO())
