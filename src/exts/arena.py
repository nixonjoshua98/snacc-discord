

import itertools
import asyncio

import datetime as dt

from discord.ext import commands, tasks

from pymongo import InsertOne, DeleteMany

from src.aboapi import API

from src import inputs
from src.structs import TextPage
from src.common import DarknessServer, checks


class Arena(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		if not self.bot.debug:
			print("Starting loop: Arena")

			self.background_loop.start()

	async def cog_check(self, ctx):
		if ctx.guild.id != DarknessServer.ID:
			raise commands.DisabledCommand("This command is disabled in this server")

		return True

	@tasks.loop(hours=8.0)
	async def background_loop(self):
		await asyncio.sleep(60 * 60 * 8.0)

		channel = self.bot.get_channel(DarknessServer.ABO_CHANNEL)

		if missing := await self.update_members():
			await channel.send(f"Missing username: {', '.join(missing)}")

		await channel.send("Updated stats :thumbsup:")

	@checks.snaccman_only()
	@commands.command(name="update")
	async def update_stats(self, ctx):
		""" Update the users history. Pulls from the API. """

		message = await ctx.send("Updating users data...")

		if missing := await self.update_members():
			await ctx.send(f"Missing username: {', '.join(missing)}")

		await message.edit(content="Updated stats :thumbsup:")

	@commands.command(name="stats", aliases=["s"])
	async def stats(self, ctx):
		""" View the stats of the entire guild. """

		pages = await self.create_history(include_discord=not ctx.author.is_on_mobile())

		await inputs.send_pages(ctx, pages)

	@commands.command(name="trophies", aliases=["rating"])
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the guild leaderboard. """

		async def query():
			return await self.get_member_rows()

		await inputs.show_leaderboard(
			ctx,
			"Guild Leaderboard",
			columns=["level", "rating"],
			order_by="rating",
			query_func=query
		)

	async def get_member_rows(self):
		role = self.bot.get_guild(DarknessServer.ID).get_role(DarknessServer.ABO_ROLE)

		ids = tuple(member.id for member in role.members)

		rows = await self.bot.mongo.find("arena", {"user": {"$in": ids}}).to_list(length=None)

		rows.sort(key=lambda r: (r["user"], r["date"]))

		entries = []

		for key, group in itertools.groupby(rows, key=lambda r: r["user"]):
			group = list(group)

			entries.append(group[-1])

		return sorted(entries, key=lambda e: (e.get("rating", 0), e["level"]), reverse=True)

	async def create_history(self, *, include_discord: bool = True):
		async def create_history_row(user):
			stats = await self.bot.mongo.find("arena", query).to_list(length=None)

			if stats:
				for i in range(len(stats)):
					stats[i]["rating"] = stats[i].get("rating", stats[i].get("trophies", 0))

				oldest, newest = stats[0], stats[-1]

				r = dict(name=str(user), abo_name=abo_name, level=newest["level"], rating=newest["rating"])

				r.update(rating_gained=newest['rating']-oldest['rating'], levels_gained=newest['level']-oldest['level'])

				return r

			return None

		svr = self.bot.get_guild(DarknessServer.ID)

		role = svr.get_role(DarknessServer.ABO_ROLE)

		one_week_ago = dt.datetime.utcnow() - dt.timedelta(days=7)

		data = []

		for member in role.members:

			player_entry = await self.bot.mongo.find_one("players", {"_id": member.id})

			if (abo_name := player_entry.get("abo_name")) is None:
				continue

			query = {"user": member.id, "date": {"$gte": one_week_ago}}

			if (row := await create_history_row(member)) is not None:
				data.append(row)

		data = sorted(data, key=lambda e: e["rating_gained"], reverse=True)

		pages, chunks = [], [data[i:i + 15] for i in range(0, len(data), 15)]

		# - Create pages for the history
		for chunk in chunks:
			headers = ["Name", "Discord", "Level", "Rating"] if include_discord else ["Name", "Level", "Rating"]

			page = TextPage(title="Darkness Arena History", headers=headers)

			for ele in chunk:
				lvl = f"{ele['level']}({ele['levels_gained']})"
				rating = f"{ele['rating']}({ele['rating_gained']})"

				row = [ele["abo_name"], lvl, rating]

				if include_discord:
					row.insert(1, ele["name"])

				page.add(row)

			pages.append(page.get())

		return pages

	async def update_members(self):
		svr = self.bot.get_guild(DarknessServer.ID)

		role = svr.get_role(DarknessServer.ABO_ROLE)

		missing, requests = [], []

		one_month_ago = dt.datetime.utcnow() - dt.timedelta(days=31)

		for member in role.members:
			player_entry = await self.bot.mongo.find_one("players", {"_id": member.id})

			if (abo_name := player_entry.get("abo_name")) is not None:
				player = await API.leaderboard.get_player(abo_name)

				if player is not None:
					row = dict(user=member.id, date=dt.datetime.utcnow(), level=player.level, rating=player.rating)

					requests.append(InsertOne(row))

				else:
					print(f"Warning: User {abo_name} could not be updated.")

				continue

			missing.append(member.mention)

			await asyncio.sleep(2.5)

		requests.append(DeleteMany({"date": {"$lt": one_month_ago}}))

		await self.bot.mongo.bulk_write("arena", requests)

		return missing


def setup(bot):
	bot.add_cog(Arena(bot))
