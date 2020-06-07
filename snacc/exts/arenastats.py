import discord
import asyncio

from discord.ext import commands

from datetime import datetime

from snacc.common import checks, ABO_CHANNEL
from snacc.common.emoji import Emoji
from snacc.common.queries import ArenaStatsSQL
from snacc.common.converters import UserMember, NormalUser

from snacc.structs.menus import Menu
from snacc.structs.leaderboards import TrophyLeaderboard


def chunk_list(ls, n):
	for i in range(0, len(ls), n):
		yield ls[i: i + n]


class ArenaStats(commands.Cog, name="Arena Stats"):
	""" Commands related to the Arena mode. """

	def __init__(self, bot):
		self.bot = bot

		asyncio.create_task(self.shame_users())

	async def cog_check(self, ctx):
		return await checks.has_role(ctx, key="member_role") or await checks.has_role(ctx, name="VIP")

	@staticmethod
	async def set_users_stats(ctx, target: discord.Member, level: int, trophies: int):
		"""
		Add a new stat entry for the user and limit the number of stat entries for the user in the database.

		:param ctx: Discord context, we get the bot from it.
		:param target: The user whose stats we are updating
		:param level: The level of the user
		:param trophies: The amount of trophies they have
		"""

		async with ctx.bot.pool.acquire() as con:
			async with con.transaction():
				await con.execute(ArenaStatsSQL.INSERT_ROW, target.id, datetime.now(), level, trophies)

				results = await con.fetch(ArenaStatsSQL.SELECT_USER, target.id)

				# Limit the number of user entries in the database
				if len(results) > 24:
					for result in results[24:]:
						await con.execute(ArenaStatsSQL.DELETE_ROW, target.id, result["date_set"])

	async def shame_users(self):
		while not self.bot.is_closed():
			await asyncio.sleep(60 * 60 * 8)

			for channel_id in (ABO_CHANNEL,):
				channel = self.bot.get_channel(channel_id)

				if channel is None:
					continue

				conf = await self.bot.get_server(channel.guild)
				role = channel.guild.get_role(conf["member_role"])

				if role is None:
					continue

				rows = await self.bot.pool.fetch(ArenaStatsSQL.SELECT_ALL_USERS_LATEST)
				data = {row["user_id"]: row for row in rows}

				lacking, missing = [], []

				# Iterate over every member who has the role
				for member in role.members:
					user_data = data.get(member.id)

					# User has never set their stats before
					if user_data is None:
						missing.append(member.mention)
						continue

					days = (datetime.now() - user_data["date_set"]).days

					# User has not set stats recently
					if days >= 7:
						lacking.append((member.mention, days))

				message = ""

				if missing:
					message = "**__Missing__** - Set your stats `!s <level> <trophies>`\n" + ", ".join(missing)

				if lacking:
					lacking.sort(key=lambda row: row[1], reverse=True)

					message = message + "\n" * 2 if message else message

					ls = [f"{ele[0]} **({ele[1]})**" for ele in lacking]

					message += "**__Lacking__** - No recent stat updates\n" + ", ".join(ls)

				if message:
					await channel.send(message)

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="set", aliases=["s"], cooldown_after_parsing=True)
	async def set_stats(self, ctx, level: int, trophies: int):
		""" Update your ABO stats, which are visible on the leaderboard. """

		await self.set_users_stats(ctx, ctx.author, level, trophies)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.cooldown(1, 60, commands.BucketType.user)
	@commands.has_permissions(administrator=True)
	@commands.command(name="setuser", aliases=["su"], cooldown_after_parsing=True)
	async def set_user_stats_command(self, ctx, target: UserMember(), level: int, trophies: int):
		""" [Admin] Set another users ABO stats. """

		await self.set_users_stats(ctx, target, level, trophies)

		await ctx.send(f"**{target.display_name}** :thumbsup:")

	@commands.has_permissions(administrator=True)
	@commands.command(name="members")
	async def get_num_members(self, ctx):
		""" [Admin] Count the number of users who have the server member role. """

		conf = await self.bot.get_server(ctx.guild)
		role = ctx.guild.get_role(conf["member_role"])

		await ctx.send(f"Members: {len(role.members)}")

	@commands.command(name="stats")
	async def get_stats(self, ctx, target: NormalUser() = None):
		""" View your own or another members recorded arena stats. """

		target = ctx.author if target is None else target
		results = await ctx.bot.pool.fetch(ArenaStatsSQL.SELECT_USER, target.id)

		if not results:
			return await ctx.send("I found no stats for you.")

		embeds = []
		chunks = tuple(chunk_list(results, 6))
		today = datetime.today().strftime('%d/%m/%Y %X')

		for i, page in enumerate(chunks):
			embed = discord.Embed(title=f"{target.display_name}'s Arena Stats", colour=discord.Color.orange())

			embed.set_thumbnail(url=target.avatar_url)
			embed.set_footer(text=f"{ctx.bot.user.name} | Page {i + 1}/{len(chunks)}", icon_url=ctx.bot.user.avatar_url)

			for row in page:
				name = row["date_set"].strftime("%d/%m/%Y")
				value = f"**{Emoji.XP} {row['level']:02d} :trophy: {row['trophies']:,}**"

				embed.add_field(name=name, value=value)

			embeds.append(embed)

		if len(embeds) == 1:
			embeds[0].set_footer(text=f"{ctx.bot.user.name} | {today}", icon_url=ctx.bot.user.avatar_url)

		await Menu(embeds, timeout=60, delete_after=False).send(ctx)

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="trophies")
	async def show_leaderboard(self, ctx: commands.Context):
		""" Show the server trophy leaderboard. """

		await TrophyLeaderboard().send(ctx)


def setup(bot):
	bot.add_cog(ArenaStats(bot))
