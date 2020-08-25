
from discord.ext import commands

from src import inputs


class Bank(commands.Cog):

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance(s). """

		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		usd, btc = bank.get("usd", 0), bank.get("btc", 0)

		await ctx.send(f"You have **${usd:,}** and **{btc:,}** BTC")

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
