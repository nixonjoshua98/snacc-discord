from discord.ext import commands

from src.structures import ServerGameStats
from src.structures import PlayerGameStats

from src.common import checks
from src.common import backup
from src.common import constants
from src.common import asycio_schedule


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

	@commands.command(name="stats", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		player = PlayerGameStats(ctx.guild, ctx.author.id)

		player.update_stats(level=level, trophies=trophies, write_file=True)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.command(name="lb", aliases=["lbt"])
	async def show_guild_trophy_leaderboard(self, ctx):
		server = ServerGameStats(ctx.guild)

		await ctx.send(server.create_leaderboard(sort_by="trophies"))

	@commands.is_owner()
	@commands.command(name="shame")
	async def shame(self, ctx):
		await ctx.send(self.get_shame_message(ctx.guild))

	async def background_shame_task(self):
		guild = self.bot.get_guild(constants.GUILD_ID)

		channel = guild.get_channel(constants.BOT_SPAM_CHANNEL)

		await channel.send(self.get_shame_message(guild))

	@staticmethod
	def get_shame_message(guild) -> str:
		server = ServerGameStats(guild)

		members = server.get_slacking_members()

		message = "**Lacking Activity**\n"
		message += " ".join(tuple(map(lambda m: m.member.mention, members)))

		return message




