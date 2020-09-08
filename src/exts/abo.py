import discord

from discord.ext import commands

from src.aboapi import API

from src.common import DarknessServer

from src.structs.confirm import Confirm


class ABO(commands.Cog):
	__help_verify_checks__ = True

	async def cog_check(self, ctx):
		if ctx.guild.id != DarknessServer.ID:
			raise commands.DisabledCommand("This command is disabled in this server")

		return True

	@commands.is_owner()
	@commands.command(name="aboname")
	async def set_abo_name(self, ctx, user: discord.Member, *, name):
		""" Associate a discord user to a user in ABO. """

		embed = ctx.bot.embed(title="Auto Battles Online", description=f"{user.mention} username is `{name}`?")

		if not await Confirm(embed).prompt(ctx):
			return await ctx.send("Operation aborted.")

		await ctx.bot.db["players"].update_one({"_id": user.id}, {"$set": {"abo_name": name}}, upsert=True)

		await ctx.send(f"Username has been set to `{name}`")

	@commands.group(name="info", hidden=True, invoke_without_command=True)
	async def info_group(self, ctx):
		""" ... """

	@info_group.command(name="player")
	async def get_player(self, ctx, *, name):
		""" Show information about a player. """

		player = await API.leaderboard.get_player(name)

		if player is None:
			return await ctx.send(f"I found no player named `{name}`")

		guild = player.guild if player.guild is not None else 'N/A'

		embed = ctx.bot.embed(title=f"{player.name} [Guild: {guild}]")

		embed.description = (
			f"Rank: **#{player.rank:02d}**\n"
			f"Level: **{player.level:,}**\n"
			f"Rating: **{player.rating:,}**\n"
		)

		await ctx.send(embed=embed)

	@info_group.command(name="guild")
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
