

import discord
import asyncio
import itertools

import datetime as dt

from discord.ext import commands, tasks

from pymongo import InsertOne, DeleteMany

from src.aboapi import API

from src import inputs
from src.common import DarknessServer, checks
from src.common.errors import IncorrectUsername
from src.common.converters import Range

from src.structs import Confirm


class Arena(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.start_shame_users()

	async def cog_check(self, ctx):
		if ctx.guild.id != DarknessServer.ID:
			raise commands.DisabledCommand("This command is disabled in this server")

		return True

	async def get_member_rows(self):
		role = self.bot.get_guild(DarknessServer.ID).get_role(DarknessServer.ABO_ROLE)

		ids = tuple(member.id for member in role.members)

		rows = await self.bot.mongo.find("arena", {"user": {"$in": ids}}).to_list(length=None)

		rows.sort(key=lambda r: (r["user"], r["date"]))

		entries = []

		for key, group in itertools.groupby(rows, key=lambda r: r["user"]):
			group = list(group)

			entries.append(group[-1])

		return sorted(entries, key=lambda e: e["level"], reverse=True)

	@staticmethod
	async def set_users_stats(ctx, user: discord.Member, level, rating):
		one_month_ago = dt.datetime.utcnow() - dt.timedelta(days=31)

		row = dict(user=user.id, date=dt.datetime.utcnow(), level=level)

		if rating is not None:
			row["rating"] = rating

		requests = [InsertOne(row), DeleteMany({"user": user.id, "date": {"$lt": one_month_ago}})]

		await ctx.bot.mongo.bulk_write("arena", requests)

	def start_shame_users(self):

		async def predicate():
			if not self.bot.debug:
				print("Starting loop: Shame")

				await asyncio.sleep(60 * 60 * 6)

				self.shame_users_loop.start()

		asyncio.create_task(predicate())

	async def create_shame_message(self):
		now = dt.datetime.utcnow()

		rows = await self.get_member_rows()

		data = {row["user"]: row for row in rows}

		shamed_members = []

		darkness_server = self.bot.get_guild(DarknessServer.ID)

		darkness_role = darkness_server.get_role(DarknessServer.ABO_ROLE)

		for member in darkness_role.members:
			user_data = data.get(member.id)

			if user_data is None:
				shamed_members.append((member.mention, None))

			elif (last_update := (now - user_data["date"]).days) >= 7:
				shamed_members.append((member.mention, last_update))

		if shamed_members:
			shamed_members.sort(key=lambda row: row[1] or -1, reverse=True)

			ls = []

			for m in shamed_members:
				ls.append(f"{m[0]}" + (f"**({m[1]})**" if m[1] is not None else ""))

			return "**__Lacking__** - No recent stat updates\n" + ", ".join(ls)

		return None

	@tasks.loop(hours=12.0)
	async def shame_users_loop(self):
		""" Background tasks which posts to the main server. """

		channel = self.bot.get_channel(DarknessServer.ABO_CHANNEL)

		if (message := await self.create_shame_message()) is not None:
			await channel.send(message)

	@checks.snaccman_only()
	@commands.command(name="shame")
	async def shame(self, ctx):
		""" Posts the shame message. """

		if (message := await self.create_shame_message()) is not None:
			await ctx.send(message)

		else:
			await ctx.send("Everyone is up-to-date!")

	@commands.cooldown(1, 3_600, commands.BucketType.user)
	@commands.command(name="set", aliases=["s"], cooldown_after_parsing=True, usage="<level> <rating>")
	async def set_stats(self, ctx, level: Range(1, 250) = None, rating: Range(0, 10_000) = None):
		""" Update your arena stats. Stats are used to track activity and are displayed on the leaderboard. """

		player = await ctx.bot.mongo.find_one("players", {"_id": ctx.author.id})

		if player.get("abo_name") is not None:
			player_inst = await API.leaderboard.get_player(player["abo_name"])

			if player_inst is not None:
				await self.set_users_stats(ctx, ctx.author, level, rating)

				await ctx.send(f"**{player['abo_name']}** :thumbsup:")

			else:
				raise IncorrectUsername("I failed to pull your data from the game. Contact my owner")

		elif level is None:
			await ctx.send("Trying to automate your stats? Talk to my owner.")

		else:
			await self.set_users_stats(ctx, ctx.author, level, rating)

			await ctx.send(f"**{str(ctx.author)}** :thumbsup:")

	@commands.command(name="lvls")
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the server level leaderboard. """

		async def query():
			return await self.get_member_rows()

		await inputs.show_leaderboard(
			ctx,
			"Guild Leaderboard",
			columns=["level", "rating"],
			order_by="rating",
			query_func=query
		)


def setup(bot):
	bot.add_cog(Arena(bot))
