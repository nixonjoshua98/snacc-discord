from discord.ext import commands

from src.common import myjson


class Backup(commands.Cog, command_attrs=dict(hidden=True), name="backup"):
	def __init__(self, bot):
		self.bot = bot

	@commands.is_owner()
	@commands.command(name="backup")
	async def backup(self, ctx):
		myjson.backup_all_files()

		await ctx.send(f"**Done** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="restore")
	async def restore(self, ctx):
		myjson.download_all_files()

		await ctx.send(f"**Done** :thumbsup:")