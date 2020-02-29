import discord

from discord.ext import commands

from src.structures import ServerGameStats
from src.structures import PlayerGameStats

from src.common import checks
from src.common import myjson


class GameStats(commands.Cog):
	FILE = "game_stats.json"

	def __init__(self, bot):
		self.bot = bot

		myjson.download_file(self.FILE)

	async def cog_check(self, ctx):
		return await checks.in_rank_room(ctx) and await checks.has_member_role(ctx) and commands.guild_only()

	@checks.id_exists_in_file(FILE)
	@commands.command(name="me", help="Display your own stats")
	async def get_stats(self, ctx):
		stats = PlayerGameStats(ctx.author)
		await ctx.send(embed=stats.create_embed())

	@commands.command(name="set", aliases=["s"], help="Set your game stats")
	async def set_stats(self, ctx, level: int, trophies: int):
		PlayerGameStats(ctx.author).update(level=level, trophies=trophies)
		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", hidden=True)
	async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
		stats = PlayerGameStats(user)
		stats.update(level=level, trophies=trophies)
		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.command(name="lb", help="Show guild trophy leaderboard")
	async def leaderboard(self, ctx):
		server = ServerGameStats(ctx.guild)
		await ctx.send(server.create_leaderboard())

	@commands.is_owner()
	@commands.command(name="shame", hidden=True)
	async def shame(self, ctx):
		server = ServerGameStats(ctx.guild)
		await ctx.send(server.create_shame_message())



