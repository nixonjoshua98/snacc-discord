from discord.ext import commands

from src.common import backup
from src.common import checks


class Misc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_any_bot_channel(ctx) and commands.guild_only()

	@commands.command(name="69")
	async def help(self, ctx):
		help_text = "Help Command"

		await ctx.send(help_text)

	@commands.is_owner()
	@commands.command(name="backup")
	async def backup(self, ctx):
		backup.backup_all_files()

		await ctx.send(f"Backup done :smile:")
