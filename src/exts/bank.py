import random

from discord.ext import commands

from src import inputs
from src.common.converters import DiscordUser


class Bank(commands.Cog):

	@commands.cooldown(1, 3_600 * 24, commands.BucketType.user)
	@commands.command(name="daily")
	async def daily(self, ctx):
		""" Gain your daily rewards. """

		money = random.randint(5_000, 10_000)

		await ctx.bot.mongo.increment_one("bank", {"id": ctx.author.id}, {"usd": money})

		await ctx.send(f"You have received **${money:,}**")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance(s). """

		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		usd, btc = bank.get("usd", 0), bank.get("btc", 0)

		msg = f"You have **${usd:,}** and **{btc:,}** BTC"

		await ctx.send(msg)

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal_coins(self, ctx, *, target: DiscordUser()):
		""" Attempt to steal from another user. """

		# - Get data
		author_bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})
		target_bank = await ctx.bot.mongo.find_one("bank", {"_id": target.id})

		# - Calculate stolen amount
		min_money, max_money = int(target_bank.get("usd", 0) * 0.025), int(target_bank.get("usd", 0) * 0.075)

		stolen_amount = random.randint(max(1, min_money), max(1, max_money))

		stolen_amount = min(author_bank.get("usd", 0), stolen_amount)

		thief_tax = int(stolen_amount // random.uniform(2.0, 8.0)) if stolen_amount >= 2_500 else 0

		# - Update database
		await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": stolen_amount - thief_tax})
		await ctx.bot.mongo.decrement_one("bank", {"_id": target.id}, {"usd": stolen_amount})

		s = f"You stole **${stolen_amount:,}** from **{target.display_name}!**"

		if thief_tax > 0:
			s = s[0:-3] + f" **but the thief you hired took a cut of **${thief_tax:,}**."

		await ctx.send(s)

	@commands.cooldown(1, 15, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		async def query():
			return await ctx.bot.mongo.find("bank").sort("usd", -1).to_list(length=100)

		await inputs.show_leaderboard(
			ctx,
			"Richest Players",
			columns=["usd"],
			order_by="usd",
			headers=["Money"],
			query_func=query
		)


def setup(bot):
	bot.add_cog(Bank())
