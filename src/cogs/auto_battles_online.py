import discord

from discord.ext import commands
from datetime import datetime

from src.common import (FileReader,)
from src.common import (checks, myjson, errors)

from src.common.constants import MAX_DAYS_NO_UPDATE

class AutoBattlesOnline(commands.Cog, name="abo"):
	FILE = "game_stats.json"

	def __init__(self, bot):
		self.bot = bot

		myjson.download_file(self.FILE)

	async def cog_check(self, ctx):
		return (
				await checks.in_abo_channel(ctx) and
				await checks.has_member_role(ctx)
		)

	@commands.command(name="me", help="Display your own stats")
	async def get_stats(self, ctx: commands.Context):
		with FileReader("game_stats.json") as file:
			stats = file.get(str(ctx.author.id), default_val=None)

			# Never set stats before
			if stats is None:
				msg = f"**{ctx.author.display_name}** you need to set your stats first :slight_smile:"

				raise errors.AutoBattlesStatsError(msg)

		embed = discord.Embed(title=ctx.author.display_name, description=f"Auto Battles Online", color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)
		embed.set_footer(text="Darkness Family")

		for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
			embed.add_field(name=txt, value=stats[i], inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="set", aliases=["s"], help="Set your game stats")
	async def set_stats(self, ctx, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today().strftime("%d/%m/%Y %H:%M:%S"), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", hidden=True)
	async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today().strftime("%d/%m/%Y %H:%M:%S"), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.command(name="lb", help="Show guild trophy leaderboard")
	async def leaderboard(self, ctx):
		members = await self.get_members(ctx)

		if not members:
			return await ctx.send("Not enough data :frowning:")

		members.sort(key=lambda ele: ele[-1][-1], reverse=True)

		name_length = 15

		msg = f"```c++\n{ctx.guild.name} Leaderboard\n"
		msg += f"\n    Username{' ' * (name_length - 7)}Lvl Trophies"

		rank = 1

		# Create the leaderboard
		for member, stats in members:
			date, level, trophies = stats

			days_ago = (datetime.today() - datetime.strptime(date, "%d/%m/%Y %H:%M:%S")).days
			username_gap = " " * (name_length - len(member.display_name)) + " "

			msg += f"\n#{rank:02d} {member.display_name[0:name_length]}"
			msg += f"{username_gap}{level:03d} {trophies:04d}"
			msg += f" {days_ago} days ago" if days_ago >= MAX_DAYS_NO_UPDATE else ""

			rank += 1

		msg += "```"

		await ctx.send(msg)

	@staticmethod
	async def get_members(ctx: commands.Context) -> list:
		with FileReader("server_settings.json") as f:
			member_role_id = f.get(ctx.guild.id, {}).get("member_role", None)

		member_role = discord.utils.get(ctx.guild.roles, id=member_role_id)

		if member_role is None:
			return []

		members = []

		# Load the members with stats
		with FileReader("game_stats.json") as file:
			for member in ctx.guild.members:

				# Ignore non-members
				if member_role not in member.roles:
					continue

				stats = file.get(str(member.id), default_val=None)

				if stats is not None:
					members.append((member, stats))

		return members


