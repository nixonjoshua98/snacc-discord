import discord
import os

from discord.ext import commands

from src import cogs
from src.common import (myjson, asycio_schedule)
from src.common import FileReader

class MyBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.prefix, case_insensitive=True)

	async def on_ready(self):
		await self.wait_until_ready()

		print("Bot successfully started")

		for c in cogs.ALL_COGS:
			print(f"Added Cog: {c.__name__}")

			self.add_cog(c(self))

		asycio_schedule.add_task(60 * 5, myjson.backup_background_task, 60 * 5)

	async def on_command_error(self, ctx, esc):
		return await ctx.send(esc)

	async def on_message(self, message: discord.Message):
		if os.getenv("DEBUG", False) and not await self.is_owner(message.author):
			return

		# Ignore DMs
		if message.guild is None:
			return

		# Ignore itself
		elif message.author.id == self.user.id:
			return

		await self.process_commands(message)

	def prefix(self, bot:commands.Bot, message: discord.message):
		with FileReader("server_settings.json") as f:
			data = f.get(str(message.guild.id), default_val={})

		return data.get("prefix", "!")

	def run(self):
		super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")