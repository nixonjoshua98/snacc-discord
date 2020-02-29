import discord
import os

from src import cogs
from src.common import myjson
from src.common import asycio_schedule
from src.common.constants import SNACC_ID

from discord.ext import commands


class MyBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix="!", case_insensitive=True)

	async def on_ready(self):
		await self.wait_until_ready()

		print("Bot successfully started")

		for c in cogs.ALL_COGS:
			self.add_cog(c(self))

			print(f"Added Cog: {c.__name__}")

		asycio_schedule.add_task(60, myjson.backup_background_task, 60 * 3)

	async def on_command_error(self, ctx, esc):
		if isinstance(esc, commands.CommandOnCooldown):
			return await ctx.send(f"**{ctx.author.display_name}** you are on cooldown :frowning:")

		return await ctx.send(esc)

	async def on_message(self, message: discord.Message):
		if os.getenv("DEBUG", False) and message.author.id != SNACC_ID:
			return

		elif message.author.id == self.user.id:
			return

		elif message.content.startswith(self.command_prefix):
			await self.process_commands(message)

	def run(self):
		super().run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")