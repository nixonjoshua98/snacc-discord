from discord.ext import commands
from src.structures.guild_member import GuildMember
from src.structures.server_member_stats import ServerMemberStats
from src.common import checks
from src.common import backup
from src.common import constants


class Stats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		backup.download_file("stats.json")

	async def cog_check(self, ctx):
		return (
				await checks.in_bot_channel(ctx) and
				await checks.has_member_role(ctx) and
				await checks.message_from_guild(ctx)
		)

	@commands.command(name="me")
	async def get_stats(self, ctx):
		embed = GuildMember(_id=ctx.author.id, display_name=ctx.author.display_name).create_embed()

		if embed is not None:
			await ctx.send(embed=embed)
		else:
			await ctx.send(f"**{ctx.author.display_name}**, I found no stats for you")

	@commands.command(name="stats", aliases=["s"])
	async def set_stats(self, ctx, level: int, trophies: int):
		GuildMember(_id=ctx.author.id).update_stats(level=level, trophies=trophies, write_file=True)

		backup.upload_file("stats.json")

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.command(name="lb", aliases=["lbt"])
	async def show_guild_trophy_leaderboard(self, ctx):
		await ctx.send(ServerMemberStats(ctx.guild).create_leaderboard(sort_by="trophies"))

	async def shame_background_task(self):
		guild = self.bot.get_guild(constants.GUILD_ID)
		channel = guild.get_channel(constants.BOT_SPAM_CHANNEL)

		shame_members = ServerMemberStats(guild).get_members_no_updates(3)

		message = "**Lacking Activity**\n"
		message += " ".join(tuple(map(lambda m: guild.get_member(m.id).mention, shame_members)))

		await channel.send(message)





