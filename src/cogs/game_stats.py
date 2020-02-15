from discord.ext import commands

from src.structures import ServerGameStats
from src.structures import PlayerGameStats

from src.structures import Member

from src.common import checks
from src.common import backup
from src.common import asycio_schedule

from src.common.constants import GUILD_ID, BOT_SPAM_CHANNEL


class GameStats(commands.Cog):
	FILE = "game_stats.json"
	SHAME_COMMAND_DELAY = 60 * 60 * 6

	def __init__(self, bot):
		self.bot = bot

		backup.download_file(self.FILE)

		asycio_schedule.add_task(self.SHAME_COMMAND_DELAY, self.background_shame_task)

	async def cog_check(self, ctx):
		return (
				await checks.in_bot_channel(ctx) and
				await checks.has_member_role(ctx) and
				commands.guild_only()
		)

	@checks.id_exists_in_file(FILE)
	@commands.command(name="me")
	async def get_stats(self, ctx):
		player = PlayerGameStats(ctx.guild, ctx.author.id)

		await ctx.send(embed=player.create_embed())

	@commands.command(name="set", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		player = Member(ctx.author.id)

		updated = player.update_game_stats(level=level, trophies=trophies)

		await ctx.send(f"**{ctx.author.display_name}** {':thumbsup:' if updated else ':thumbsdown:'}")

	@commands.is_owner()
	@commands.command(name="setuser", aliases=["su"])
	async def set_user(self, ctx, _id: int, level: int, trophies: int):
		player = Member(_id)

		updated = player.update_game_stats(level=level, trophies=trophies)

		member_set = ctx.guild.get_member(_id)

		display_name = member_set.display_name if member_set else ctx.author.display_name

		await ctx.send(f"**{display_name}** {':thumbsup:' if updated else ':thumbsdown:'}")

	@commands.command(name="lb")
	async def leaderboard(self, ctx):
		server = ServerGameStats(ctx.guild)

		await ctx.send(server.create_leaderboard(ctx.author.id))

	@commands.is_owner()
	@commands.command(name="shame")
	async def shame(self, ctx):
		await ctx.send(self.create_shame_message(ctx.guild))

	async def background_shame_task(self):
		guild = self.bot.get_guild(GUILD_ID)

		channel = guild.get_channel(BOT_SPAM_CHANNEL)

		print("Posted members with lacking activity")

		await channel.send(self.create_shame_message(guild))

	@staticmethod
	def create_shame_message(guild) -> str:
		server = ServerGameStats(guild)

		members = server.get_slacking_members()

		message = "**Lacking Activity**\n"
		message += " ".join(tuple(map(lambda m: m.member.mention, members)))

		return message




