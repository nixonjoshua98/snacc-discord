

import discord
import asyncio
import itertools

import datetime as dt

from discord.ext import commands, tasks

from pymongo import InsertOne, DeleteMany

from src import inputs
from src.common import DarknessServer, checks
from src.common.converters import Range


class ABO(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		#self.start_shame_users()

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

		return sorted(entries, key=lambda e: e["trophies"], reverse=True)

	@staticmethod
	async def set_users_stats(ctx, user: discord.Member, level, trophies):
		"""
		Add a new stat entry for the user and limit the number of stat entries for the user in the database.

		:param ctx: Discord context, we get the bot from it.
		:param user: The user whose stats we are updating
		:param level: The level of the user
		:param trophies: The amount of trophies they have
		"""

		six_months_ago = dt.datetime.utcnow() - dt.timedelta(weeks=26)

		row = dict(user=user.id, date=dt.datetime.utcnow(), level=level, trophies=trophies)

		requests = [InsertOne(row), DeleteMany({"user": user.id, "date": {"$lt": six_months_ago}})]

		await ctx.bot.mongo.bulk_write("arena", requests)

	def start_shame_users(self):

		async def predicate():
			if not self.bot.debug:
				print("Starting loop: Shame")

				await asyncio.sleep(60 * 60 * 6)

				self.shame_users_loop.start()

		asyncio.create_task(predicate())

	async def create_shame_message(self):
		""" Create the shame message for the guild (attached to `destination`). """

		server = self.bot.get_guild(DarknessServer.ID)

		rows = await self.get_member_rows()

		data = {row["user"]: row for row in rows}

		lacking, missing = [], []

		now = dt.datetime.utcnow()

		role = server.get_role(DarknessServer.ABO_ROLE)

		for member in role.members:

			user_data = data.get(member.id)

			# No data could be found in the database
			if user_data is None:
				missing.append(member.mention)

			else:
				days = (now - user_data["date"]).days

				if days >= 7:
					lacking.append((member.mention, days))

		message = None

		if missing:
			message = f"**__Missing__** - Set your stats `!s <level> <trophies>`\n"
			message += ", ".join(missing)

		if lacking:
			lacking.sort(key=lambda row: row[1], reverse=True)

			message = message + "\n" * 2 if message is not None else ""

			ls = [f"{ele[0]} **({ele[1]})**" for ele in lacking]

			message += "**__Lacking__** - No recent stat updates\n" + ", ".join(ls)

		return message

	@tasks.loop(hours=12.0)
	async def shame_users_loop(self):
		""" Background tasks which posts to the main server. """

		channel = self.bot.get_channel(DarknessServer.ABO_CHANNEL)

		if (message := await self.create_shame_message()) is not None:
			await channel.send(message)

	@checks.snaccman_only()
	@checks.main_server_only()
	@commands.command(name="shame")
	async def shame(self, ctx):
		""" Posts the shame message. """

		if (message := await self.create_shame_message()) is not None:
			await ctx.send(message)

		else:
			await ctx.send("Everyone is up-to-date!")

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="set", aliases=["s"], cooldown_after_parsing=True)
	async def set_stats(self, ctx, level: Range(1, 125), trophies: Range(1, 10_000)):
		""" Update your arena stats. Stats are used to track activity and are displayed on the trophy leaderboard. """

		await self.set_users_stats(ctx, ctx.author, level, trophies)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"])
	async def set_user_stats_command(self, ctx, level: int, trophies: int, *, target: discord.Member):
		""" Set another users ABO stats. """

		await self.set_users_stats(ctx, target, level, trophies)

		await ctx.send(f"**{target.display_name}** :thumbsup:")

	@commands.command(name="stats")
	async def get_stats(self, ctx, *, target: discord.Member = None):
		""" View your own or another members recorded arena stats. """

		target = ctx.author if target is None else target

		results = await ctx.bot.mongo.find("arena", {"user": target.id}).sort("date", -1).to_list(length=15)

		if not results:
			return await ctx.send(f"I found nothing for {target.display_name}.")

		embed = ctx.bot.embed(title=f"{target.display_name}'s Arena Stats")

		for result in results:
			date = result["date"].strftime("%d/%m/%Y")

			level, trophies = f"{result['level']:,}", f"{result['trophies']:,}"

			embed.add_field(name=date, value=f":trophy: {trophies}")

		await ctx.send(embed=embed)

	@commands.command(name="trophies")
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the server trophy leaderboard. """

		async def query():
			return await self.get_member_rows()

		await inputs.show_leaderboard(
			ctx,
			"Trophy Leaderboard",
			columns=["level", "trophies"],
			order_by="trophies",
			query_func=query,
			max_rows=None
		)


def setup(bot):
	bot.add_cog(ABO(bot))
