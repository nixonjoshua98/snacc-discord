

import discord
import asyncio

import datetime as dt

from discord.ext import commands, tasks

from src import inputs
from src.common import MainServer, checks
from src.common.emoji import Emoji
from src.common.models import ArenaStatsM
from src.common.converters import Range


def chunk_list(ls, n):
	for i in range(0, len(ls), n):
		yield ls[i: i + n]


MAX_ROWS_PER_USER = 24
PING_COOLDOWN = 7
NO_PING_ROLE = "Free Agent"


class ArenaStats(commands.Cog, name="Arena Stats", command_attrs=(dict(cooldown_after_parsing=True))):
	def __init__(self, bot):
		self.bot = bot

		self.start_shame_users()

	async def cog_check(self, ctx):
		return ctx.guild.id in (MainServer.ID, 720798797004931153)

	@staticmethod
	async def set_users_stats(ctx, user: discord.Member, level, trophies):
		"""
		Add a new stat entry for the user and limit the number of stat entries for the user in the database.

		:param ctx: Discord context, we get the bot from it.
		:param user: The user whose stats we are updating
		:param level: The level of the user
		:param trophies: The amount of trophies they have
		"""

		async with ctx.bot.pool.acquire() as con:
			await con.execute(ArenaStatsM.INSERT_ROW, user.id, dt.datetime.utcnow(), level, trophies)

			results = await con.fetch(ArenaStatsM.SELECT_USER, user.id)

			if len(results) > MAX_ROWS_PER_USER:
				for result in results[MAX_ROWS_PER_USER:]:
					await con.execute(ArenaStatsM.DELETE_ROW, user.id, result["date_set"])

	def start_shame_users(self):
		"""
		Start the `shame_users_loop` asyncio task loop assuming that the bot is not in DEBUG mode and that Snaccman
		is the owner of the bot.
		"""

		async def predicate():
			if not self.bot.debug and await self.bot.is_snacc_owner():
				print("Starting loop: Shame")

				await asyncio.sleep(60 * 60 * 6)

				self.shame_users_loop.start()

		asyncio.create_task(predicate())

	async def create_shame_message(self, channel: discord.TextChannel):
		""" Create the shame message for the guild (attached to `destination`). """

		conf = await self.bot.get_server_config(channel.guild)

		role = channel.guild.get_role(conf["member_role"])

		if role is None:
			return

		rows = await self.bot.pool.fetch(ArenaStatsM.SELECT_LATEST_MEMBERS, tuple(m.id for m in role.members))

		data = {row["user_id"]: row for row in rows}

		lacking, missing = [], []

		now = dt.datetime.utcnow()

		for member in role.members:
			no_ping_role = discord.utils.get(member.roles, name=NO_PING_ROLE)

			if no_ping_role is not None:
				continue

			user_data = data.get(member.id)

			# No data could be found in the database
			if user_data is None:
				missing.append(member.mention)

			else:
				days = (now - user_data["date_set"]).days

				if days >= PING_COOLDOWN:
					lacking.append((member.mention, days))

		message = None

		if missing:
			message = f"**__Missing__** - Set your stats `{conf['prefix']}s <level> <trophies>`\n" + ", ".join(missing)

		if lacking:
			lacking.sort(key=lambda row: row[1], reverse=True)

			message = message + "\n" * 2 if message is not None else ""

			ls = [f"{ele[0]} **({ele[1]})**" for ele in lacking]

			message += "**__Lacking__** - No recent stat updates\n" + ", ".join(ls)

		return message if message is not None else "Everyone is up-to-date!"

	@tasks.loop(hours=12.0)
	async def shame_users_loop(self):
		""" Background tasks which posts to the main server. """

		channel = self.bot.get_channel(MainServer.ABO_CHANNEL)

		message = await self.create_shame_message(channel)

		await channel.send(message)

	@checks.snaccman_only()
	@checks.main_server_only()
	@commands.command(name="shame")
	async def shame(self, ctx):
		""" Posts the shame message. """

		message = await self.create_shame_message(ctx.channel)

		await ctx.send(message)

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="set", aliases=["s"])
	async def set_stats(self, ctx, level: Range(1, 125), trophies: Range(1, 10_000)):
		""" Update your arena stats. Stats are used to track activity and are displayed on the trophy leaderboard. """

		await self.set_users_stats(ctx, ctx.author, level, trophies)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.cooldown(1, 60, commands.BucketType.user)
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

		results = await ctx.bot.pool.fetch(ArenaStatsM.SELECT_USER, target.id)

		if not results:
			return await ctx.send(f"I found nothing for {target.display_name}.")

		embeds, chunks = [], tuple(chunk_list(results, 6))

		for i, page in enumerate(chunks):
			embed = discord.Embed(title=f"{target.display_name}'s Arena Stats", colour=discord.Color.orange())

			embed.set_thumbnail(url=target.avatar_url)
			embed.set_footer(text=f"{str(ctx.bot.user)} | Page {i + 1}/{len(chunks)}", icon_url=ctx.bot.user.avatar_url)

			for row in page:
				date_set = row["date_set"].strftime("%d/%m/%Y")

				stats = f"{Emoji.XP} **{row['level']:02d}** :trophy: **{row['trophies']:,}**"

				embed.add_field(name=date_set, value=stats)

			embeds.append(embed)

		await inputs.send_pages(ctx, embeds)

	@commands.cooldown(1, 15, commands.BucketType.guild)
	@commands.command(name="trophies")
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the server trophy leaderboard. """

		async def query():
			svr_config = await ctx.bot.get_server_config(ctx.guild)

			role = ctx.guild.get_role(svr_config["member_role"])

			return await ctx.bot.pool.fetch(ArenaStatsM.SELECT_LEADERBOARD, tuple(member.id for member in role.members))

		await inputs.show_leaderboard(
			ctx,
			"Trophy Leaderboard",
			columns=["level", "trophies"],
			order_by="trophies",
			query_func=query,
			max_rows=60
		)


def setup(bot):
	bot.add_cog(ArenaStats(bot))
