
from discord.ext import commands

import datetime as dt


DAILY_REWARDS = [
	{"bank": {"btc": 1}}, 		{"bank": {"usd": 1_500}}, 			{"bank": {"usd": 3_000}},
	{"bank": {"usd": 5_000}}, 	{"bank": {"btc": 1, "usd": 1_000}}, {"bank": {"usd": 7_500}},
	{"bank": {"usd": 10_000}}, 	{"bank": {"btc": 1}}, 				{"bank": {"usd": 5_000}}
]


class Rewards(commands.Cog):
	@commands.cooldown(1, 3_600 * 24, commands.BucketType.user)
	@commands.command(name="daily")
	async def daily(self, ctx):
		""" Collect your rewards every 24 hours. """

		now = dt.datetime.utcnow()

		player_row = await ctx.bot.mongo.find_one("players", {"_id": ctx.author.id})

		last_daily = player_row.get("last_daily", now)
		daily_streak = player_row.get("daily_streak", 0)

		hours_since_daily = (now - last_daily).total_seconds() / 3600

		# - First day or streak ended
		if hours_since_daily == 0 or hours_since_daily >= 48:
			daily_streak = 1

			daily_reward = DAILY_REWARDS[0]

		# - Next day
		elif hours_since_daily >= 24:
			daily_reward = DAILY_REWARDS[daily_streak % len(DAILY_REWARDS)]

			daily_streak += 1

		# - Cooldown
		else:
			cd = last_daily.replace(tzinfo=dt.timezone.utc).timestamp()

			bucket = self.daily._buckets.get_bucket(ctx.message)

			# - Very smelly...
			bucket._last, bucket._window, bucket._tokens = cd, cd, 0

			raise commands.CommandOnCooldown(bucket, 24 * 3_600 - (now - last_daily).total_seconds())

		reward_text = []

		# - Create the message format and update the database with the rewards.
		for col, rewards in daily_reward.items():
			await ctx.bot.mongo.increment_one(col, {"_id": ctx.author.id}, rewards)

			for item, amount in rewards.items():
				if item == "usd":
					reward_text.append(f"**${amount:,}**")

				elif item == "btc":
					reward_text.append(f"**{amount:,} BTC**")

		# - Update the database
		await ctx.bot.mongo.update_one(
			"players",
			{"_id": ctx.author.id},
			{"daily_streak": daily_streak, "last_daily": now}
		)

		# - Create message
		message_text = (
			f"You are on a **{daily_streak}** day streak! "
			f"You have received {', '.join(reward_text[:-1])}"
			f"{f' and {reward_text[-1]}' if len(reward_text) > 1 else f'{reward_text[0]}'}!"
		)

		await ctx.send(message_text)


def setup(bot):
	bot.add_cog(Rewards())
