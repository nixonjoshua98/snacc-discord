from discord.ext import commands

from src.structures import GuildMember
from src.structures import ServerMemberStats

from src.common import checks
from src.common import backup
from src.common import constants
from src.common import asycio_schedule


class Stats(commands.Cog):
	SHAME_COMMAND_DELAY = 60 * 60 * 8

	def __init__(self, bot):
		self.bot = bot

		backup.download_file("stats.json")

		self.start_background_tasks()

	def start_background_tasks(self):
		asycio_schedule.add_task(self.SHAME_COMMAND_DELAY, self.background_shame_task)

	async def cog_check(self, ctx):
		return (
				await checks.in_bot_channel(ctx) and
				await checks.has_member_role(ctx) and
				await checks.message_from_guild(ctx)
		)

	@commands.command(name="me")
	@commands.check(checks.user_has_stats)
	async def get_stats(self, ctx):
		embed = GuildMember(_id=ctx.author.id, display_name=ctx.author.display_name).create_embed()

		await ctx.send(embed=embed)

	@commands.command(name="stats", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		GuildMember(_id=ctx.author.id).update_stats(level=level, trophies=trophies, write_file=True)

		backup.upload_file("stats.json")

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.command(name="lb", aliases=["lbt"])
	async def show_guild_trophy_leaderboard(self, ctx):
		await ctx.send(ServerMemberStats(ctx.guild).create_leaderboard(sort_by="trophies"))

	@commands.is_owner()
	@commands.command(name="shame")
	async def shame(self, ctx):
		await ctx.send(self.get_shame_message(ctx.guild))

	async def background_shame_task(self):
		guild = self.bot.get_guild(constants.GUILD_ID)
		channel = guild.get_channel(constants.BOT_SPAM_CHANNEL)

		message = self.get_shame_message(guild)

		await channel.send(message)

	@staticmethod
	def get_shame_message(guild) -> str:
		shame_members = ServerMemberStats(guild).get_members_no_updates(3)

		message = "**Lacking Activity**\n"
		message += " ".join(tuple(map(lambda m: guild.get_member(m.id).mention, shame_members)))

		return message




