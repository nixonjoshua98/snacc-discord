import random

from discord.ext import commands

from src import inputs


class Bank(commands.Cog):
	@commands.cooldown(1, 3_600 * 24, commands.BucketType.user)
	@commands.command(name="daily")
	async def daily(self, ctx):
		""" Gain your daily rewards. """

		money = random.randint(5_000, 10_000)

		await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": money})

		await ctx.send(f"You have received **${money:,}**")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance(s). """

		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		usd, btc = bank.get("usd", 0), bank.get("btc", 0)

		msg = f"You have **${usd:,}** and **{btc:,}** BTC"

		await ctx.send(msg)

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
