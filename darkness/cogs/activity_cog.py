import discord

from datetime import datetime

from darkness.common import data_reader
from darkness.common import myjson

from discord.ext import commands


class Activity(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.has_role("Darkness Employee")
	@commands.command(name="active", aliases=["a"], description="Register your level and trophies")
	async def set_stats_command(self, ctx, level: int = None, trophies: int = None):
		username = ctx.author.display_name

		# If no arguments passed
		if level is None or trophies is None or level <= 0 or trophies <= 0:
			row = self.get_latest_row(username)

			# A row was found
			if row:
				embed = discord.Embed(
					title=f"Member: {username}",
					description=f"Most Recent Stat Update",
					color=0xff8000,
				)

				embed.add_field(name="Date Recorded", value=row[0])
				embed.add_field(name="Level", value=row[1])
				embed.add_field(name="No. Trophies", value=row[2])

				embed.set_footer(text=self.bot.user.display_name)

				await ctx.send(embed=embed)

			# Row wasn't found, most likely because the user hasn't set anything before.
			else:
				await ctx.send(f"``{username}``, I could not find any stats for you")

		# Only allow stat sets if a member has a nickname (of their IGN)
		elif ctx.author.nick is None:
			await ctx.send(f"``{username}``, you need a nickname to be able to set your stats")

		elif ctx.author.nick is not None:
			updated_stats = await self.update_stats(username, level, trophies)

			if updated_stats:
				await ctx.send(f"``{username}`` has successfully updated their stats")

			elif not updated_stats:
				await ctx.send(f"``{username}``, you can only update your stats once a day")

		myjson.upload("member_activity.json")

	@staticmethod
	async def update_stats(username: str, level: int, trophies: int) -> bool:
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

		data_to_add = [today_str, level, trophies]

		data_reader.append_json_keys("member_activity.json", username, data_to_add)

		return True

	@staticmethod
	def get_latest_row(username):
		activity_file = data_reader.read_json("member_activity.json")

		member_record = activity_file.get(username, [[]])

		return member_record[-1]

