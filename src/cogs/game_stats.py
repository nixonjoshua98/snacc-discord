from discord.ext import commands

from src.structures import GuildMember
from src.structures import GuildServer

from src.common import checks
from src.common import backup


class GameStats(commands.Cog):
	FILE = "game_stats.json"

	def __init__(self, bot):
		self.bot = bot

		backup.download_file(self.FILE)

	async def cog_check(self, ctx):
		return (
				await checks.in_bot_channel(ctx) and
				await checks.has_member_role(ctx) and
				commands.guild_only()
		)

	@checks.id_exists_in_file(FILE)
	@commands.command(name="me")
	async def get_stats(self, ctx):
		player = GuildMember(ctx.author.id, ctx.guild)

		await ctx.send(embed=player.create_stat_embed())

	@commands.command(name="set", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		player = GuildMember(ctx.author.id, ctx.guild)

		updated = player.update_game_stats(level=level, trophies=trophies)

		await ctx.send(f"**{ctx.author.display_name}** {':thumbsup:' if updated else ':thumbsdown:'}")

	@commands.is_owner()
	@commands.command(name="setuser", aliases=["su"])
	async def set_user(self, ctx, _id: int, level: int, trophies: int):
		player = GuildMember(_id, ctx.guild)

		updated = player.update_game_stats(level=level, trophies=trophies)

		member_set = ctx.guild.get_member(_id)

		display_name = member_set.display_name if member_set else ctx.author.display_name

		await ctx.send(f"**{display_name}** {':thumbsup:' if updated else ':thumbsdown:'}")

	@commands.command(name="lb")
	async def leaderboard(self, ctx):
		server = GuildServer(ctx.guild)

		await ctx.send(server.create_leaderboard())

	@commands.is_owner()
	@commands.command(name="shame")
	async def shame(self, ctx):
		server = GuildServer(ctx.guild)

		message = "**Lacking Activity**\n"
		message += " ".join(tuple(map(lambda m: m.member.mention, server.slacking)))

		await ctx.send(message)



