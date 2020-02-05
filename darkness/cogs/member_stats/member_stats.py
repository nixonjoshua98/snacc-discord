
import os
import operator

from discord.ext import commands

from darkness.common import backup
from darkness.common import checks

from darkness.common.constants import BOT_SPAM_CHANNEL, GUILD_ID

from .member_stats_funcs import (
	add_stat_entry,
	create_user_stat_embed,
	create_leaderboard,
	get_all_members_latest_stats,
	get_inactive_members
)


class MemberStats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		backup.download_file("member_stats.json")

	@commands.check(checks.can_use_command)
	@commands.command(name="stats", aliases=["s"], description="Set your stats ``!s <lvl> <trophies>``")
	async def set_user_own_stats(self, ctx, level: int, trophies: int):
		updated = add_stat_entry(ctx.author.id, level, trophies)

		if not os.getenv("DEBUG", False):
			backup.upload_file("member_stats.json")

		emoji = ":thumbsup:" if updated else ":thumbsdown:"

		await ctx.send(f"``{ctx.author.display_name}`` {emoji}")

	@commands.check(checks.can_use_command)
	@commands.command(name="me", description="Shows your latest stats")
	async def get_user_own_stats(self, ctx):
		embed = create_user_stat_embed(ctx.author)

		if embed is None:
			await ctx.send(f"No stats found for {ctx.author.display_name}")

		else:
			embed.set_footer(text=self.bot.user.display_name)

			await ctx.send(embed=embed)

	@commands.check(checks.can_use_command)
	@commands.command(name="lbd", description="Show member stats sorted by last update date")
	async def get_date_lb(self, ctx):
		stats = get_all_members_latest_stats(ctx.guild)

		stats.sort(key=lambda row: row[1], reverse=False)

		msg = create_leaderboard(stats, "date")

		await ctx.send(msg)

	@commands.check(checks.can_use_command)
	@commands.command(name="lbl", description="Show member stats sorted by level")
	async def get_level_lb(self, ctx):
		stats = get_all_members_latest_stats(ctx.guild)

		stats.sort(key=operator.itemgetter(2), reverse=True)

		msg = create_leaderboard(stats, "level")

		await ctx.send(msg)

	@commands.check(checks.can_use_command)
	@commands.command(name="lbt", description="Show member stats sorted by trophies")
	async def get_trophy_lb(self, ctx):
		stats = get_all_members_latest_stats(ctx.guild)

		stats.sort(key=operator.itemgetter(3), reverse=True)

		msg = create_leaderboard(stats, "trophies")

		await ctx.send(msg)

	async def shame(self):
		guild = self.bot.get_guild(GUILD_ID)

		channel = guild.get_channel(BOT_SPAM_CHANNEL)

		members = get_inactive_members(channel.guild)

		message = "**Lacking Activity**\n" + " ".join(tuple(map(lambda m: m.mention, members)))

		await channel.send(message)




