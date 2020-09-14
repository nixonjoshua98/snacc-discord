import re
import discord

from discord.ext import commands

from src import utils

from src.aboapi import API

from src.common import DarknessServer

from src.structs.confirm import Confirm
from src.structs.textpage import TextPage
from src.structs.dynamicpages import DynamicPages


class ABO(commands.Cog):
	__help_verify_checks__ = True

	async def cog_check(self, ctx):
		if ctx.guild.id not in (DarknessServer.ID,):
			raise commands.DisabledCommand("This command is disabled in this server")

		return True

	@commands.is_owner()
	@commands.command(name="setaboname")
	async def set_abo_name(self, ctx, user: discord.Member, *, name):
		""" Associate a discord user to an abo username. """

		embed = ctx.bot.embed(title="Auto Battles Online", description=f"{user.mention} username is `{name}`?")

		if not await Confirm(embed).prompt(ctx):
			return await ctx.send("Operation aborted.")

		await ctx.bot.db["players"].update_one({"_id": user.id}, {"$set": {"abo_name": name}}, upsert=True)

		await ctx.send(f"Username has been set to `{name}`")

	@commands.command(name="getdiscord")
	async def get_discord(self, ctx, *, username):
		""" Get the discord user associated with an abo username. """

		player = await ctx.bot.db["players"].find_one({"abo_name": re.compile(username, re.IGNORECASE)})

		if player is None:
			await ctx.send("I do not have a reference to their discord stored.")

		else:
			if (user := ctx.guild.get_member(player["_id"])) is not None:
				await ctx.send(f"The user **{player['abo_name']}** is associated with **{str(user)}**")

			else:
				await ctx.send("I found the user in my records but they are not in this server.")

	@commands.group(name="abo", hidden=True, invoke_without_command=True)
	async def group(self, ctx):
		""" ... """

	@group.command(name="guild")
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

		embed.add_field(name="Guild XP", value=f"{guild.guild_xp}/{guild.total_guild_xp}")

		await ctx.send(embed=embed)

	@group.command(name="guilds")
	async def show_guild_leaderboard(self, ctx):
		""" Show the guild leaderboard. """

		async def callback(current: int, change, pages: list):
			return await self.dynamic_leaderboard_callback(create_page, current, change, pages)

		async def create_page(start, end):
			guilds = await API.leaderboard.get_guilds(pos=start, count=end)

			embed = ctx.bot.embed(title="Guild Leaderboard", author=ctx.author)

			desc = []

			for guild in guilds:
				name_len = 20 - len(str(guild.rank)) - 1

				s = f"#{guild.rank} {guild.name: <{name_len}} {guild.rating:,}"

				desc.append(s)

			embed.description = "```" + "\n".join(desc) + "```"

			return embed if len(guilds) > 0 else None

		await DynamicPages([await create_page(0, 15)], callback).send(ctx)

	@group.command(name="player")
	async def get_player(self, ctx, *, name):
		""" Show information about a player. """

		player = await API.leaderboard.get_player(name)

		if player is None:
			return await ctx.send(f"I found no player named `{name}`")

		embed = ctx.bot.embed(title=f"{player.name} [Guild: {player.guild}]")

		embed.description = (
			f"Rank: **#{player.rank:02d}**\n"
			f"Level: **{player.level:,}**\n"
			f"Rating: **{player.rating:,}**\n"
		)

		embed.add_field(name="Last Active", value=player.last_active)
		embed.add_field(name="Guild XP", value=f"{player.guild_xp}/{player.total_guild_xp}")

		await ctx.send(embed=embed)

	@group.command(name="players")
	async def show_player_leaderboard(self, ctx):
		""" Show the player leaderboard. """

		async def callback(current: int, change, pages: list):
			return await self.dynamic_leaderboard_callback(create_page, current, change, pages)

		async def create_page(start, end):
			players = await API.leaderboard.get_players(pos=start, count=end)

			embed = ctx.bot.embed(title="Player Leaderboard", author=ctx.author)

			desc = []

			for player in players:
				name_len = 20 - len(str(player.rank)) - 1

				s = f"#{str(player.rank): <4} {player.name: <{name_len}} {player.level} {player.rating:,}"

				desc.append(s)

			embed.description = "```" + "\n".join(desc) + "```"

			return embed if len(players) > 0 else None

		await DynamicPages([await create_page(0, 15)], callback).send(ctx)

	@staticmethod
	async def dynamic_leaderboard_callback(create_page, current: int, change, pages: list):
		new_index = current + change

		if change == 1 and (new_index + 1) >= len(pages):
			page = await create_page(new_index * 15, 15)

			if page is None:
				return current

			pages.append(page)

		return max(0, new_index)


def setup(bot):
	bot.add_cog(ABO())
