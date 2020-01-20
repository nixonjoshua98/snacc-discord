import discord
import dataclasses

from datetime import datetime

from darkness.common import data_reader
from darkness.common import myjson

from discord.ext import commands


@dataclasses.dataclass()
class StatsDC:
	username: str
	date: str
	level: int
	trophies: int


class Activity(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.has_role("Darkness Employee")
	@commands.command(name="stats", aliases=["s"], description="Register your level and trophies")
	async def stats_command(self, ctx, *args):
		if len(args) == 0:
			await self.display_own_stats(ctx)

		elif len(args) == 1:
			await self.display_others_stats(ctx, args[0])

		elif len(args) == 2:
			await self.update_own_stats(ctx, args)

	@commands.is_owner()
	@commands.command(name="remove", hidden=True)
	async def remove_member(self, ctx, username: str):
		data_reader.remove_json_key("member_activity.json", username)

		await ctx.send(f"Removed ``{username}`` from member stats")

	@commands.command(name="all", description="Show all registered users")
	async def all_stats(self, ctx):
		data = data_reader.read_json("member_activity.json")

		msg = "```Members\n"

		for k in data:
			stats = self.get_stats(k)

			msg += f"{stats.username}\n"
			msg += f"\tLvl: {stats.level} Trophies: {stats.trophies}\n"

		msg += "```"

		await ctx.send(msg)

	async def display_own_stats(self, ctx):
		username = ctx.author.display_name

		stats = self.get_stats(username)

		if stats is not None:
			embed = self.create_embed(username, stats)

			await ctx.send(embed=embed)
		else:
			await ctx.send(f"``{username}``, I could not find any stats for you")

	async def display_others_stats(self, ctx, username):
		stats = self.get_stats(username)

		if stats is not None:
			embed = self.create_embed(stats.username, stats)

			await ctx.send(embed=embed)
		else:
			await ctx.send(f"I could not find any stats for ``{username}``")

	async def update_own_stats(self, ctx, args):
		username = ctx.author.display_name

		# Check if all args are ints
		if all(map(str.isdigit, args[0: 2])):
			level, trophies = args[0: 2]

			stats_updated = self.set_stats(username, int(level), int(trophies))

			if stats_updated:
				await ctx.send(f"``{username}`` has successfully updated their stats")

			elif not stats_updated:
				await ctx.send(f"``{username}``, you can only update your stats once a day")

			myjson.upload("member_activity.json")

	def create_embed(self, username, stats):
		embed = discord.Embed(
			title=f"Member: {username}",
			description=f"Most Recent Stat Update",
			color=0xff8000,
		)

		embed.add_field(name="Date Recorded", value=str(stats.date))
		embed.add_field(name="Level", value=str(stats.level))
		embed.add_field(name="No. Trophies", value=str(stats.trophies))

		embed.set_footer(text=self.bot.user.display_name)

		return embed

	@staticmethod
	def set_stats(username: str, level: int, trophies: int) -> bool:
		today = datetime.today()

		activity_file = data_reader.read_json("member_activity.json")
		member_record = activity_file.get(username, None)

		if member_record is not None:
			row_date, row_level, row_trophies = member_record[-1]
			date_object = datetime.strptime(row_date, "%m-%d-%Y")
			days_since = (today - date_object).days

			# Limit updates to once per day
			if days_since < 1:
				return False

		today_str = today.strftime("%m-%d-%Y")

		data_reader.append_json_keys("member_activity.json", username, [today_str, level, trophies])

		return True

	@staticmethod
	def get_stats(username):
		activity_file = data_reader.read_json("member_activity.json")

		for k, v in activity_file.items():
			if k.lower() == username.lower():
				v[-1].insert(0, k)

				s = StatsDC(*v[-1])

				return s

		return None

