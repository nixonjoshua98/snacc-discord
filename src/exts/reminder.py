import asyncio

import datetime as dt

import src.utils as utils

from discord.ext import commands, tasks

from src.common.converters import TimePeriod

from src.common.models import RemindersM


class Reminder(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.__set_reminders = dict()

		if not self.bot.debug:
			print("Starting Loop: Reminders")
			self.remind_loop.start()

	def create_reminder_task(self, row):
		async def remind_task(_id, user, chnl, seconds):
			await asyncio.sleep(seconds)

			chnl = self.bot.get_channel(chnl)
			user = self.bot.get_user(user)

			if chnl is not None and user is not None:
				await utils.msg.send(chnl, f"{user.mention} :alarm_clock:")

			await self.bot.pool.execute(RemindersM.DELETE_ROW, _id)

		_id, chnl_id = row["reminder_id"], row["channel_id"]

		if _id not in self.__set_reminders:
			sleep_time = max(1, (row["remind_end"] - dt.datetime.utcnow()).total_seconds())

			self.__set_reminders[_id] = asyncio.create_task(remind_task(_id, _id, chnl_id, sleep_time))

	@commands.group(name="remind", invoke_without_command=True)
	async def remind_me(self, ctx, *, period: TimePeriod() = None):
		"""
View your reminder or create a new one.
Usage: `!remind <56s/14m/5d>`

"""

		reminder = await RemindersM.fetchrow(ctx.bot.pool, ctx.author.id, insert=False)

		if period is None and reminder is None:
			await ctx.send("You do not have any active reminders")

		elif reminder is not None:
			await ctx.send("Remindme")

		else:
			now = dt.datetime.utcnow()

			row = await ctx.pool.fetchrow(RemindersM.INSERT_ROW, ctx.author.id, ctx.channel.id, now, now + period)

			self.create_reminder_task(row)

			await ctx.send(f"I will remind you in `{period}`")

	@remind_me.command(name="cancel")
	async def cancel_reminder(self, ctx):
		""" Cancel your current reminder. """

		reminder = await RemindersM.fetchrow(ctx.bot.pool, ctx.author.id, insert=False)

		if reminder is None:
			await ctx.send("You do not have any active reminders")

		else:
			if reminder["reminder_id"] in self.__set_reminders:
				task = self.__set_reminders[reminder["reminder_id"]]

				task.cancel()

				try:
					await task
				except asyncio.CancelledError:
					self.__set_reminders.pop(reminder["reminder_id"], None)

					await self.bot.pool.execute(RemindersM.DELETE_ROW, reminder["reminder_id"])

					await ctx.send("Your reminder has been cancelled.")

				else:
					await ctx.send("Your reminder could not be cancelled.")

	@tasks.loop(minutes=30.0)
	async def remind_loop(self):
		for row in await self.bot.pool.fetch(RemindersM.SELECT_ALL):
			now = dt.datetime.utcnow()

			seconds_until_end = (row["remind_end"] - now).total_seconds()

			if row["reminder_id"] in self.__set_reminders:
				continue

			elif seconds_until_end <= (30 * 60):
				self.create_reminder_task(row)


def setup(bot):
	bot.add_cog(Reminder(bot))
