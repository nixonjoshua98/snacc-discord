import discord
import asyncio

import datetime as dt

from discord.ext import commands, tasks

from pymongo import InsertOne, DeleteMany

from src.aboapi import API

from src.common import checks, DarknessServer

from src.structs import TextPage
from src.structs.displaypages import DisplayPages


class Darkness(commands.Cog):
	__help_verify_checks__ = True

	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		if ctx.guild.id != DarknessServer.ID:
			raise commands.DisabledCommand("This command is disabled in this server")

		return True

	@commands.Cog.listener("on_startup")
	async def on_startup(self):

		@tasks.loop(hours=1.0)
		async def update_users_loop():
			if missing_usernames := await self.update_users():
				chnl = self.bot.get_channel(DarknessServer.BOT_CHANNEL)

				snacc = chnl.guild.owner.mention

				await chnl.send(f"{snacc}, missing usernames: {', '.join(map(lambda m: m.mention, missing_usernames))}")

		if not self.bot.debug:
			print("Starting Loop: Darkness")

			update_users_loop.start()

	@checks.in_server(DarknessServer.ID)
	@commands.command(name="trophies", aliases=["rating"])
	async def show_guild(self, ctx, *, role: discord.Role = None):
		""" Show the guild history, sorted by player rating. """

		pages = await self.create_guild_page(ctx, role=role, sort_by="rating")

		await DisplayPages(pages).send(ctx)

	@checks.in_server(DarknessServer.ID)
	@commands.has_role(DarknessServer.DARKNESS_ROLE)
	@commands.command(name="history")
	async def show_history(self, ctx, *, role: discord.Role = None):
		""" Show the guild history, sorted by the rating gained the past week. """

		pages = await self.create_guild_page(ctx, role=role, sort_by="rating_diff")

		await DisplayPages(pages).send(ctx)

	async def update_users(self):
		svr = self.bot.get_guild(DarknessServer.ID)

		role = svr.get_role(DarknessServer.DARKNESS_ROLE)

		now = dt.datetime.utcnow()

		requests, missing_usernames = [], []

		for member in role.members:
			player = await self.bot.db["players"].find_one({"_id": member.id}) or dict()

			if (abo_name := player.get("abo_name")) is not None:
				if (player := await API.leaderboard.get_player(abo_name)) is not None:
					row = dict(
						user=member.id,
						date=now,
						level=player.level,
						rating=player.rating,
						guild_xp=player.total_guild_xp
					)

					requests.append(InsertOne(row))

			else:
				missing_usernames.append(member)

		requests.append(DeleteMany({"date": {"$lt": now - dt.timedelta(days=31)}}))

		await self.bot.db["arena"].bulk_write(requests)

		await self.bot.db["abo_history"].bulk_write(requests)

		return missing_usernames

	async def create_guild_page(self, ctx, *, role, sort_by="rating_diff"):
		one_week_ago = dt.datetime.utcnow() - dt.timedelta(days=7)

		role = ctx.guild.get_role(role.id if role is not None else DarknessServer.DARKNESS_ROLE)

		ids = [m.id for m in role.members]

		stats = await ctx.bot.db["arena"].aggregate(
			[
				{
					"$match": {
						"user": {"$in": ids}, "$and": [{"date": {"$gte": one_week_ago}}]}
				},
				{
					"$sort": {"date": 1}
				},
				{
					"$group": {
						"_id": "$user",

						"level": {"$last":  "$level"}, "old_level": {"$first": "$level"},

						"rating": {"$last":  "$rating"}, "old_rating": {"$first": "$rating"},
					}
				},

				{
					"$lookup": {
						"from": "players",
						"localField": "_id",
						"foreignField": "_id",
						"as": "player"
					}
				},
				{
					"$unwind": "$player"
				},
				{
					"$project": {
						"level": 1, "rating": 1, "abo_name": "$player.abo_name",

						"levels_diff": {"$subtract": ["$level", "$old_level"]},
						"rating_diff": {"$subtract": ["$rating", "$old_rating"]}
					}
				}
			]

		).to_list(length=None)

		stats = sorted(stats, key=lambda ele: ele[sort_by], reverse=True)

		pages, chunks = [], [stats[i:i + 15] for i in range(0, len(stats), 15)]

		for chunk in chunks:
			page = TextPage(title="Guild Members history", headers=["Username", "XP", "Level", "Rating"])

			for row in chunk:
				page_row = [row["abo_name"], "0(0)", row["level"], f"{row['rating']}({row['rating_diff']})"]

				page.add(page_row)

			pages.append(page.get())

		return pages


def setup(bot):
	bot.add_cog(Darkness(bot))
