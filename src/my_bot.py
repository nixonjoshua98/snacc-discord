import asyncio
import discord
import os

from src import cogs
from src import msg_commands
from src.common import backup
from src.common import asycio_schedule
from src.common.constants import BACKUP_DELAY, MEMBER_CHANNELS, SNACC_ID

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
		if esc is commands.CommandOnCooldown:
			await ctx.send(f"**{ctx.author.display_name}** You cannot do that yet")

		else:
			await ctx.send(esc)

	async def on_message(self, message: discord.Message):
		if os.getenv("DEBUG", False) and message.author.id != SNACC_ID:
			return

		# Ignore itself
		if message.author.id == self.user.id:
			return

		# Valid commands
		elif message.content.startswith(self.command_prefix):
			await self.process_commands(message)

		# Random commands on messages
		elif message.channel.id in MEMBER_CHANNELS:
			await msg_commands.on_message_commands(message)

	def run(self):
		super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")