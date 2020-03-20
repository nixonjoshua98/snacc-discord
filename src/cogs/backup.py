import os

from discord.ext import commands

from datetime import datetime

from src.common import jsonblob
from src.common import asycio_schedule
from src.common.constants import JSON_URL_LOOKUP, RESOURCES_DIR


class Backup(commands.Cog, command_attrs=dict(hidden=True), name="backup"):
	BACKUP_DELAY = 60 * 3

	def __init__(self, bot):
		self.bot = bot

		self._backup_task = asycio_schedule.add_task(self.BACKUP_DELAY, Backup._backup_task, self.BACKUP_DELAY)

	async def _restart_backup_task(self):
		await asycio_schedule.cancel_task(self._backup_task, "_backup_task")

		self._backup_task = asycio_schedule.add_task(self.BACKUP_DELAY, Backup._backup_task, self.BACKUP_DELAY)

	@staticmethod
	async def _backup_task():
		for file, url in JSON_URL_LOOKUP.items():
			path = os.path.join(RESOURCES_DIR, file)

			modified_date = datetime.fromtimestamp(os.path.getmtime(path))

			# Only upload the file if it has been modified since the last check
			if (datetime.today() - modified_date).total_seconds() <= Backup.BACKUP_DELAY:
				if jsonblob.upload_file(file) is True:
					print(f"Uploaded '{file}' to '{url}'")

	@commands.is_owner()
	@commands.command(name="backup")
	async def backup_command(self, ctx):
		await self._restart_backup_task()

		await Backup._backup_task()

		await ctx.send(f"**Done** :thumbsup:")