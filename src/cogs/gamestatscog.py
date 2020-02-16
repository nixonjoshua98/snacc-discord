from discord.ext import commands

from src.structures import ServerGameStats
from src.structures import PlayerGameStats

from src.common import checks
from src.common import backup


class GameStatsCog(commands.Cog):
	FILE = "game_stats.json"

	def __init__(self, bot):
		self.bot = bot

		backup.download_file(self.FILE)

	async def cog_check(self, ctx):
		return await checks.in_rank_room(ctx) and await checks.has_member_role(ctx) and commands.guild_only()

	@checks.id_exists_in_file(FILE)
	@commands.command(name="me")
	async def get_stats(self, ctx):
		stats = PlayerGameStats(ctx.author)
		await ctx.send(embed=stats.create_embed())

	@commands.command(name="set", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		PlayerGameStats(ctx.author).update(level=level, trophies=trophies)
		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", aliases=["su"])
	async def set_user(self, ctx, _id: int, level: int, trophies: int):
		stats = PlayerGameStats(ctx.guild.get_member(_id))
		stats.update(level=level, trophies=trophies)
		await ctx.send(f"**{stats.user.display_name}** :thumbsup:")

	@commands.command(name="lb")
	async def leaderboard(self, ctx):
		server = ServerGameStats(ctx.guild)
		await ctx.send(server.create_leaderboard())

	@commands.is_owner()
	@commands.command(name="shame")
	async def shame(self, ctx):
		server = ServerGameStats(ctx.guild)
		await ctx.send(server.create_shame_message())



