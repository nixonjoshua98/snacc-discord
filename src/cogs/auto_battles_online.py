import discord

from discord.ext import commands
from datetime import datetime

from src.common import (FileReader,)
from src.common import (checks, myjson, errors)

from src.common.constants import (MEMBER_ROLE_ID, MAX_DAYS_NO_UPDATE)


class AutoBattlesOnline(commands.Cog, name="abo"):
	FILE = "game_stats.json"

	def __init__(self, bot):
		self.bot = bot

		myjson.download_file(self.FILE)

	async def cog_check(self, ctx):
		return await checks.in_rank_room(ctx) and await checks.has_member_role(ctx)

	@commands.is_owner()
	@commands.command(name="cleanup", hidden=True)
	async def cleanup(self, ctx: commands.Context):
		total_removed = 0

		with FileReader("game_stats.json") as file:
			for member_id, _ in file.data().items():
				member = ctx.guild.get_member(int(member_id))

				if member is None:
					file.remove(member_id)

					total_removed += 1

		await ctx.send(f"Removed {total_removed} ex-members")

	@commands.command(name="me", help="Display your own stats")
	async def get_stats(self, ctx: commands.Context):
		with FileReader("game_stats.json") as file:
			stats = file.get(str(ctx.author.id), default_val=None)

			# Never set stats before
			if stats is None:
				raise errors.NoStatsError("No Stats")

		embed = discord.Embed(title=ctx.author.display_name, description=f"Auto Battles Online", color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
			embed.add_field(name=txt, value=stats[i], inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="set", aliases=["s"], help="Set your game stats")
	async def set_stats(self, ctx, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today(), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{ctx.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", hidden=True)
	async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today(), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.command(name="lb", help="Show guild trophy leaderboard")
	async def leaderboard(self, ctx):
		members = await self.get_members(ctx)

		members.sort(key=lambda ele: ele[-1][-1], reverse=True)

		name_length = 20

		msg = "```c++\nDarkness Family Leaderboard\n"
		msg += f"\n    Username{' ' * (name_length - 7)}Lvl Trophies"

		rank = 1

		# Create the leaderboard
		for member, stats in members:
			if stats is None:
				continue

			date, level, trophies = stats

			days_ago = (datetime.today() - datetime.strptime(date, "%d/%m/%Y %H:%M:%S")).days
			username_gap = " " * (name_length - len(member.display_name)) + " "

			msg += f"\n#{rank:02d} {member.display_name[0:name_length]}"
			msg += f"{username_gap}{level:03d} {trophies:04d}"
			msg += f" {days_ago} days ago" if days_ago >= MAX_DAYS_NO_UPDATE else ""

			rank += 1

		msg += "```"

		await ctx.send(msg)

	@commands.is_owner()
	@commands.command(name="shame", hidden=True)
	async def shame(self, ctx):
		shame_members = []
		for member, stats in await self.get_members(ctx):
			if stats is not None:
				date, level, trophies = stats
				days_ago = (datetime.today() - datetime.strptime(date, "%d/%m/%Y %H:%M:%S")).days
				if days_ago < MAX_DAYS_NO_UPDATE:
					continue

			shame_members.append(member)

		msg = "**Lacking Activity**\n" + " ".join(tuple(map(lambda m: m.mention, shame_members)))

		await ctx.send(msg)

	@staticmethod
	async def get_members(ctx) -> list:
		member_role = discord.utils.get(ctx.guild.roles, id=MEMBER_ROLE_ID)

		members = []

		# Load the members with stats
		with FileReader("game_stats.json") as file:
			for member_id in file.data():
				member = ctx.guild.get_member(int(member_id))

				# Ignore non-members
				if member is None or member_role not in member.roles:
					continue

				stats = file.get(str(member.id), default_val=None)

				members.append((member, stats))

		return members


