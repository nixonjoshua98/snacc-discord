from discord.ext import commands

import datetime as dt

from src import utils

from src.common import SupportServer


class Rewards(commands.Cog):

	@commands.cooldown(1, 3_600 * 24, commands.BucketType.user)
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="daily")
	async def daily(self, ctx):
		""" Collect your rewards every 24 hours. """

		now = dt.datetime.utcnow()

		player_row = await ctx.bot.db["players"].find_one({"_id": ctx.author.id}) or dict()

		streak = player_row.get("daily_streak", 0) + 1

		last_daily = player_row.get("last_daily")

		if last_daily is not None:
			hours_since_daily = (now - last_daily).total_seconds() / 3600

			if hours_since_daily < 24:
				cd = last_daily.replace(tzinfo=dt.timezone.utc).timestamp()

				bucket = self.daily._buckets.get_bucket(ctx.message)

				bucket._last, bucket._window, bucket._tokens = cd, cd, 0

				raise commands.CommandOnCooldown(bucket, 24 * 3_600 - (now - last_daily).total_seconds())

			elif hours_since_daily >= 48:
				streak = 1

		else:
			streak = 1

		reward = 3_000 + (750 * min(streak, 14))

		# - Add the reward to the user bank balance
		await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": reward}}, upsert=True)

		# - Update the player with the new streak and daily claim time
		await ctx.bot.db["players"].update_one(
			{"_id": ctx.author.id},
			{"$set": {"last_daily": now, "daily_streak": streak}},
			upsert=True
		)

		embed = ctx.bot.embed(
			title=f"Daily Reward!",
			description=f"Your daily reward is **$3,000** + **$750** multiplied by your streak (up to 14).",
			author=ctx.author,
			thumbnail=ctx.author.avatar_url
		)

		if not utils.author_in_support_server(ctx):
			embed.description += "\n\n" + f"Click [here]({SupportServer.LINK}) to join the support server."

		embed.add_field(name="Reward", value=f"**${reward:,}**")

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Rewards())
