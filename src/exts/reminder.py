import asyncio

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
			_id, user_id, chnl_id = row["_id"], row["user"], row["channel"]

			note_text = row.get("note", "Reminder!")

			sleep_time = max(5, (row["end"] - dt.datetime.utcnow()).total_seconds())

			await asyncio.sleep(sleep_time)

			chnl = self.bot.get_channel(chnl_id)
			user = self.bot.get_user(user_id)

			if chnl is not None and user is not None:

				# - I can message the channel
				if self.bot.has_permission(chnl, send_messages=True):
					await chnl.send(f":alarm_clock: {user.mention} {note_text}")

			await self.bot.mongo.delete_one("reminders", {"_id": _id})

			self.__set_reminders.pop(row["_id"], None)

		if row["_id"] not in self.__set_reminders:
			self.__set_reminders[row["_id"]] = asyncio.create_task(remind_task())

	@commands.command(name="remind", aliases=["r"], invoke_without_command=True)
	async def remind_me(self, ctx: commands.Context, period: TimePeriod() = None, *, note: str = None):
		""" Create a new reminder. e.g `!remind "2d 5m 17s" Make food` or view your current reminders `!r` """

		now = dt.datetime.utcnow()

		note = "Reminder!" if note is None else note

		reminders = await ctx.bot.mongo.find("reminders", {"user": ctx.author.id}).to_list(length=None)

		if period is None and not reminders:
			await ctx.send("You do not have any active reminders")

		elif "@" in note:
			await ctx.send("Reminder note cannot contain **@** to avoid mention abuse.")

		elif period is None:
			embed = ctx.bot.embed(title=f"{str(ctx.author)}: Reminders")

			for r in reminders:
				delta = r["end"].timestamp() - now.timestamp()

				delta = dt.timedelta(seconds=int(delta))

				embed.add_field(name=r["note"], value=f"`{delta}`")

			await ctx.send(embed=embed)

		elif period is not None:
			row = dict(user=ctx.author.id, channel=ctx.channel.id, end=now + period, note=note)

			await ctx.bot.mongo.insert_one("reminders", row)

			self.create_reminder_task(row)

			await ctx.send(f"I will ping you in `{period}`.")

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
