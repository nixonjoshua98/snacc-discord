import discord

from discord.ext import commands
from datetime import datetime

from src.common import FileReader
from src.common import (checks, myjson, errors, leaderboard)

class AutoBattlesOnline(commands.Cog, name="abo"):
	FILE = "game_stats.json"

	def __init__(self, bot):
		self.bot = bot

		myjson.download_file(self.FILE)

	async def cog_check(self, ctx):
		return (
				await checks.in_abo_channel(ctx) and
				await checks.has_member_role(ctx)
		)

	@commands.command(name="me", help="Display your own stats")
	async def get_stats(self, ctx: commands.Context):
		with FileReader("game_stats.json") as file:
			stats = file.get(str(ctx.author.id), default_val=None)

			# Never set stats before
			if stats is None:
				msg = f"**{ctx.author.display_name}** you need to set your stats first :slight_smile:"

				raise errors.AutoBattlesStatsError(msg)

		embed = discord.Embed(title=ctx.author.display_name, description=f"Auto Battles Online", color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)
		embed.set_footer(text="Darkness")

		for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
			embed.add_field(name=txt, value=stats[i], inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="set", aliases=["s"], help="Set your game stats")
	async def set_stats(self, ctx, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today().strftime("%d/%m/%Y %H:%M:%S"), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", hidden=True)
	async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today().strftime("%d/%m/%Y %H:%M:%S"), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.command(name="alb", help="Show guild trophy leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		"""
		Shows the ABO leaderboard

		:param ctx: The message context
		:return:
		"""
		leaderboard_string = await leaderboard.create_leaderboard(ctx.author, leaderboard.Type.ABO)

		return await ctx.send(leaderboard_string)