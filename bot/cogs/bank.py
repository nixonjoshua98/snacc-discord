import random
import discord

from discord.ext import commands

from bot.common import checks, CoinsSQL

from bot.common.converters import NotAuthorOrBotServer, IntegerRange

from bot.common.database import DBConnection

from bot.structures import CoinLeaderboard


class Bank(commands.Cog, name="bank"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.channel_has_tag(ctx, "game", self.bot.svr_cache)

	@commands.command(name="balance", aliases=["bal"], help="Display your coin count")
	async def balance(self, ctx: commands.Context):
		with DBConnection() as con:
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))

			user = con.cur.fetchone()

		balance = user.balance if user is not None else 0

		await ctx.send(f":moneybag: **{ctx.author.display_name}** has a total of **{balance:,}** coins")

	@commands.cooldown(1, 60 * 15, commands.BucketType.user)
	@commands.command(name="free", aliases=["pickup"], help="Get free coins [15m]")
	async def free(self, ctx: commands.Context):
		amount = random.randint(15, 50)

		with DBConnection() as con:
			con.cur.execute(CoinsSQL.INCREMENT, (ctx.author.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="steal", help="Attempt to steal coins [3hrs]")
	async def steal_coins(self, ctx: commands.Context, target: NotAuthorOrBotServer()):
		if random.randint(0, 3) != 0:
			return await ctx.send(f"**{ctx.author.display_name}** failed to steal from **{target.display_name}**")

		with DBConnection() as con:
			# Get author coin balance
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))

			author_coins = con.cur.fetchone()
			author_coins = author_coins.balance if author_coins is not None else 0

			# Get target coin balance
			con.cur.execute(CoinsSQL.SELECT_USER, (target.id,))

			target_coins = con.cur.fetchone()
			target_coins = target_coins.balance if target_coins is not None else 0

			# Maximum amount of coins which can be stolen
			max_coins = int(min(author_coins * 0.05, target_coins * 0.05, 1000))

			# Actual amount of coins stolen
			amount = random.randint(0, max(0, max_coins))

			# Update the users balances
			con.cur.execute(CoinsSQL.INCREMENT, (ctx.author.id, amount))
			con.cur.execute(CoinsSQL.DECREMENT, (target.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** stole **{amount:,}** coins from **{target.display_name}**")

	@commands.command(name="gift", help="Gift some coins")
	async def gift(self, ctx, target: NotAuthorOrBotServer(), amount: IntegerRange(1, 10000)):
		with DBConnection() as con:
			# Get author coins
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))

			author_coins = con.cur.fetchone()
			author_coins = author_coins.balance if author_coins is not None else 0

			# Balance check
			if author_coins < amount:
				await ctx.send(f"**{ctx.author.display_name}, you do not have enough coins for that**")

			else:
				# Update balances
				con.cur.execute(CoinsSQL.DECREMENT, (ctx.author.id, amount))
				con.cur.execute(CoinsSQL.INCREMENT, (target.id, amount))

				await ctx.send(f"**{ctx.author.display_name}** gifted **{amount:,}** coins to **{target.display_name}**")

	@commands.is_owner()
	@commands.command(name="setcoins", hidden=True)
	async def set_coins(self, ctx, user: discord.Member, amount: IntegerRange(1, 1_000_000)):
		with DBConnection() as con:
			con.cur.execute(CoinsSQL.UPDATE, (user.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.command(name="coinlb", aliases=["clb"], help="Show the server coin leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		lb = CoinLeaderboard()

		await ctx.send(lb.get(ctx.author))


def setup(bot):
	bot.add_cog(Bank(bot))