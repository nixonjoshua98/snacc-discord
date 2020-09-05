
from discord.ext import commands

from src.structs.textleaderboard import TextLeaderboard


class Bank(commands.Cog):

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance(s). """

		bank = await ctx.bot.db["bank"].find_one({"_id": ctx.author.id}) or dict()

		usd, btc = bank.get("usd", 0), bank.get("btc", 0)

		await ctx.send(f"You have **${usd:,}** and **{btc:,}** BTC")

	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		async def query():
			return await ctx.bot.db["bank"].find({}).sort("usd", -1).to_list(length=100)

		await TextLeaderboard(
			title="Richest Players",
			columns=["usd"],
			order_by="usd",
			headers=["Money"],
			query_func=query
		).send(ctx)


def setup(bot):
	bot.add_cog(Bank())
