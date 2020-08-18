import asyncio
import discord

import datetime as dt

from discord.ext import commands, tasks

from src.common.converters import TimePeriod


class Reminder(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.__set_reminders = dict()

		if not self.bot.debug:
			print("Starting Loop: Reminders")
			self.remind_loop.start()

	def create_reminder_task(self, row):
		async def remind_task():
			_id, user_id, chnl_id = row["_id"], row["_id"], row["channel"]

			note_text = row.get("note", "Reminder!")

			sleep_time = max(5, (row["end"] - dt.datetime.utcnow()).total_seconds())

			await asyncio.sleep(sleep_time)

			chnl = self.bot.get_channel(chnl_id)
			user = self.bot.get_user(user_id)

			if chnl is not None and user is not None:
				try:
					await chnl.send(f":alarm_clock: {user.mention} {note_text}")

				except (discord.HTTPException, discord.Forbidden):
					""" Failed """

			await self.bot.mongo.delete_one("reminders", {"_id": _id})

			self.__set_reminders.pop(row["_id"], None)

		if row["_id"] not in self.__set_reminders:
			self.__set_reminders[row["_id"]] = asyncio.create_task(remind_task())

	@commands.group(name="remind", invoke_without_command=True)
	async def remind_me(self, ctx: commands.Context, period: TimePeriod() = None, *, note: str = None):
		"""
View your reminder or create a new one.
e.g `!remind "2d 5m 17s" Make food`
		"""

		note = "Reminder!" if note is None else note

		reminder = await ctx.bot.mongo.find_one("reminders", {"_id": ctx.author.id})

		if period is None and not reminder:
			await ctx.send("You do not have any active reminders")

		elif "@" in note:
			await ctx.send("Reminder note cannot contain `@` to avoid mass mention abuse.")

		elif reminder:
			seconds = (reminder["end"] - dt.datetime.utcnow()).total_seconds()

			delta = dt.timedelta(seconds=int(seconds))

			await ctx.send(f"Time left on your current reminder: `{delta}`")

		elif period is not None and not reminder:
			now = dt.datetime.utcnow()

			row = dict(_id=ctx.author.id, channel=ctx.channel.id, start=now, end=now + period, note=note)

			await ctx.bot.mongo.insert_one("reminders", row)

			self.create_reminder_task(row)

			await ctx.send(f"I will ping you in `{period}`. Cancel this with `{ctx.prefix}remind cancel`")

	@remind_me.command(name="cancel")
	async def cancel_reminder(self, ctx):
		""" Cancel your current reminder. """

		reminder = await ctx.bot.mongo.find_one("reminders", {"_id": ctx.author.id})

		if not reminder:
			await ctx.send("You do not have any active reminders")

		else:
			if reminder["_id"] in self.__set_reminders:
				task = self.__set_reminders[reminder["_id"]]

				task.cancel()

				try:
					await task

				except asyncio.CancelledError:
					self.__set_reminders.pop(reminder["_id"], None)

				else:
					return await ctx.send("I failed to cancel your reminder.")

			await ctx.bot.mongo.delete_one("reminders", {"_id": ctx.author.id})

			await ctx.send("Your reminder has been cancelled.")

	@tasks.loop(minutes=30.0)
	async def remind_loop(self):
		cur = self.bot.mongo.find("reminders")

		for row in await cur.to_list(length=None):
			now = dt.datetime.utcnow()

			seconds_until_end = (row["end"] - now).total_seconds()

			if row["_id"] in self.__set_reminders:
				continue

			elif seconds_until_end <= 3600:
				self.create_reminder_task(row)


def setup(bot):
	bot.add_cog(Reminder(bot))
