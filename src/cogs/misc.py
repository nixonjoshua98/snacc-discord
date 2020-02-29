from discord.ext import commands

from src.common import backup
from src.common import checks


class Misc(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_any_bot_channel(ctx) and commands.guild_only()

	@commands.is_owner()
	@commands.command(name="backup")
	async def backup(self, ctx):
		backed_up = backup.backup_all_files()

		if backed_up:
			await ctx.send(f"Backup done :smile:")

		else:
			await ctx.send(f"Backup failed :frowning:")
