from discord.ext import commands

from src.aboapi import API

from src.structs.textpage import TextPage


class ABO(commands.Cog):
	@commands.command(name="guilds")
	async def get_guilds(self, ctx):
		""" Show the top 15 entries on the guild leaderboard. """

		guilds = await API.get_guilds(pos=0, count=15)

		page = TextPage(title="Guilds", headers=["Rank", "Name", "Rating"])

		for guild in guilds:
			row = [f"#{guild.rank:02d}", guild.name, f"{guild.rating:,}"]

			page.add(row)

		await ctx.send(page.get())

	@commands.command(name="players")
	async def get_players(self, ctx):
		""" Show the top 15 entries on the player leaderboard. """

		players = await API.get_players(pos=0, count=15)

		page = TextPage(title="Players", headers=["Rank", "Name", "Rating"])

		for player in players:
			row = [f"#{player.rank:02d}", player.name, f"{player.rating:,}"]

			page.add(row)

		await ctx.send(page.get())

	@commands.command(name="player")
	async def get_player(self, ctx, *, name):
		""" Show information about a player. """

		player = await API.get_player(name)

		if player is None:
			return await ctx.send(f"I found no player named `{name}`")

		embed = ctx.bot.embed(title=f"{player.name} [{player.guild if player.guild is not None else 'N/A'}]")

		embed.description = (
			f"Rank: **#{player.rank:02d}**\n"
			f"Level: **{player.level:,}**\n"
			f"Rating: **{player.rating:,}**"
		)

		await ctx.send(embed=embed)

	@commands.command(name="guild")
	async def get_guild(self, ctx, *, name):
		""" Show information about a guild. """

		guild = await API.get_guild(name)

		if guild is None:
			return await ctx.send(f"I found no guild named `{name}`")

		embed = ctx.bot.embed(title=f"{guild.name} [{guild.leader}]")

		embed.description = (
			f"Rank: **#{guild.rank:02d}**\n"
			f"Rating: **{guild.rating:,}**\n"
			f"Member Count: **{guild.size:,}**"
		)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(ABO())
