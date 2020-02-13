import asyncio
import discord
import random

from src import cogs
from src.common import backup
from src.common import asycio_schedule
from src.common.constants import BACKUP_DELAY

from discord.ext import commands


class MyBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix="!", case_insensitive=True)

		self.remove_command("help")

	async def background_loop(self):
		print("Background loop started")

		while not self.is_closed():
			await asyncio.sleep(60)

	async def on_ready(self):
		await self.wait_until_ready()

		print("Bot successfully started")

		for c in cogs.all:
			self.add_cog(c(self))

			print(f"Added Cog: {c.__name__}")

		self.loop.create_task(self.background_loop())

		asycio_schedule.add_task(BACKUP_DELAY, backup.backup_background_task)

	async def on_command_error(self, ctx, esc):
		await ctx.send(esc)

	async def on_message(self, message: discord.Message):
		if message.author.id == self.user.id:
			return

		if random.randint(0, 100) <= 25:
			channel, content, author = message.channel, message.content, message.author

			f = lambda c: f"*{c}*"

			msg = " ".join([f(c) if i % 2 == 1 else f(c.upper()) for i, c in enumerate(content.lower()) if c != " "])

			await channel.send(msg)

		else:
			await self.process_commands(message)

	def run(self):
		super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")