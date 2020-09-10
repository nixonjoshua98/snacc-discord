

import asyncio
import discord

import datetime as dt

from discord.ext import commands, tasks

from pymongo import InsertOne, DeleteMany

from src.aboapi import API

from src import utils

from src.common import DarknessServer

from src.structs import TextPage
from src.structs.displaypages import DisplayPages
from src.structs.textleaderboard import TextLeaderboard


class Arena(commands.Cog):
	__help_verify_checks__ = True

	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		if ctx.guild.id != DarknessServer.ID:
			raise commands.DisabledCommand("This command is disabled in this server")

		return True

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if not self.bot.debug:
			print("Starting loop: Arena")

			self.background_loop.start()

	@tasks.loop(hours=6.0)
	async def background_loop(self):
		await asyncio.sleep(60 * 60 * 6.0)

		channel = self.bot.get_channel(DarknessServer.ABO_CHANNEL)

		msg = "Updated Stats :thumbsup:"

		if missing := await self.update_members():
			msg += "\n\n" + f"**Missing usernames:** {', '.join(missing)}"

		await channel.send(msg)

	@commands.is_owner()
	@commands.command(name="update")
	async def update_stats(self, ctx):
		""" Update the users history. Pulls from the API. """

		msg = "Updated Stats :thumbsup:"

		message = await ctx.send("Updating users data...")

		if missing := await self.update_members():
			msg += "\n\n" + f"**Missing usernames:** {', '.join(missing)}"

		await message.edit(content=msg)

	@commands.command(name="stats", aliases=["s"], usage="")
	async def stats(self, ctx, *, role: discord.Role = None):
		""" View the history of the guild, or narrow it down to a single role. """

		pages = await self.create_history(ctx, role=role)

		if pages is None:
			return await ctx.send("Found no user records.")

		await DisplayPages(pages).send(ctx)

	@commands.command(name="trophies", aliases=["rating"])
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the guild leaderboard. """

		async def query():
			role = ctx.guild.get_role(DarknessServer.ABO_ROLE)

			ids = tuple(member.id for member in role.members)

			rows = await ctx.bot.db["arena"].aggregate(
				[
					{"$match": {"user": {"$in": ids}}},
					{"$group": {"_id": "$user", "level": {"$last": "$level"}, "rating": {"$last": "$rating"}}},
					{"$sort":  {"date": 1}}
				]

			).to_list(length=None)

			return sorted(rows, key=lambda e: (e["rating"], e["level"]), reverse=True)

		await TextLeaderboard(
			title="Guild Leaderboard",
			columns=["level", "rating"],
			order_by="rating",
			query_func=query
		).send(ctx)

	async def create_history(self, ctx, role=None):
		one_week_ago = dt.datetime.utcnow() - dt.timedelta(days=7)

		role = role if role is not None else ctx.guild.get_role(DarknessServer.ABO_ROLE)

		ids = [m.id for m in role.members]

		stats = await ctx.bot.db["arena"].aggregate(
			[
				{"$match": {"user": {"$in": ids}, "$and": [{"date": {"$gte": one_week_ago}}]}},
				{
					"$group": {
						"_id": "$user",
						"old_level": {"$first": "$level"}, "old_rating": {"$first": "$rating"},
						"new_level": {"$last":  "$level"}, "new_rating": {"$last":  "$rating"},
					}
				},
				{"$sort": {"date": 1}},
			]

		).to_list(length=None)

		if not stats:
			return None

		players = await ctx.bot.db["players"].find({"_id": {"$in": ids}}).to_list(length=None)

		stats.sort(key=lambda e: e["old_rating"] - e["new_rating"])

		pages, chunks = [], [stats[i:i + 15] for i in range(0, len(stats), 15)]

		on_mobile = ctx.author.is_on_mobile()

		for chunk in chunks:
			# - Hide the Discord column if on mobile since the width is too much
			headers = ["Name", "Level", "Rating"] if on_mobile else ["Name", "Discord", "Level", "Rating"]

			page = TextPage(title="Darkness Arena History", headers=headers)

			for row in chunk:
				player = utils.get(players, _id=row["_id"], default=dict())

				levels, rating = row['new_level'] - row['old_level'], row['new_rating'] - row['old_rating']

				page_row = [player.get("abo_name"), f"{row['new_level']}({levels})", f"{row['new_rating']}({rating})"]

				if not on_mobile:
					member = discord.utils.get(role.members, id=row["_id"])

					page_row.insert(1, str(member))

				page.add(page_row)

			pages.append(page.get())

		return pages

	async def update_members(self):
		role = self.bot.get_guild(DarknessServer.ID).get_role(DarknessServer.ABO_ROLE)

		missing, requests = [], []

		one_month_ago = dt.datetime.utcnow() - dt.timedelta(days=31)

		players = await self.bot.db["players"].find({"_id": {"$in": [m.id for m in role.members]}}).to_list(length=None)

		for member in role.members:
			player_entry = utils.get(players, _id=member.id, default=dict())

			if (abo_name := player_entry.get("abo_name")) is not None:
				player = await API.leaderboard.get_player(abo_name)

				if player is not None:
					row = dict(user=member.id, date=dt.datetime.utcnow(), level=player.level, rating=player.rating)

					requests.append(InsertOne(row))

				else:
					print(f"Warning: User {abo_name} could not be updated.")

				continue

			missing.append(member.mention)

			await asyncio.sleep(5.0)

		requests.append(DeleteMany({"date": {"$lt": one_month_ago}}))

		await self.bot.db["arena"].bulk_write(requests)

		return missing


def setup(bot):
	bot.add_cog(Arena(bot))
