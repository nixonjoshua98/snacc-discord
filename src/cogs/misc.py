from discord.ext import commands

from src.common import myjson
from src.common import checks


class Misc(commands.Cog, command_attrs=dict(hidden=True)):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_any_bot_channel(ctx) and commands.is_owner()

	@commands.command(name="backup")
	async def backup(self, ctx):
		myjson.backup_all_files()

		await ctx.send(f"**Done** :thumbsup:")

	@commands.command(name="restore")
	async def restore(self, ctx):
		myjson.download_all_files()

		await ctx.send(f"**Done** :thumbsup:")
