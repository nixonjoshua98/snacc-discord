import random
import discord

from discord.ext import commands

from src.common import checks, queries

from src.common.database import DBConnection

from src.structures import Leaderboard

from src.common._leaderboard import CoinLeaderboard


class Bank(commands.Cog, name="bank"):
	def __init__(self, bot):
		self.bot = bot

		self._leaderboard = Leaderboard(
			title="Coin Leaderboard",
			file="coins.json",
			columns=["coins"],
			bot=self.bot,
			sort_func=lambda kv: kv[1]["coins"]
		)

	async def cog_check(self, ctx):
		return await checks.channel_has_tag(ctx, "game", self.bot.svr_cache)

	@commands.command(name="balance", aliases=["bal"], help="Display your coin count")
	async def balance(self, ctx: commands.Context):
		with DBConnection() as con:
			con.cur.execute("SELECT balance FROM coins WHERE userID = %s", (ctx.author.id,))

			user = con.cur.fetchone()

		balance = user.balance if user is not None else 0

		await ctx.send(f":moneybag: **{ctx.author.display_name}** has a total of **{balance:,}** coins")

	@commands.cooldown(1, 60 * 15, commands.BucketType.user)
	@commands.command(name="free", aliases=["pickup"], help="Get free coins [15m]")
	async def free(self, ctx: commands.Context):
		amount = random.randint(15, 50)

		with DBConnection() as con:
			con.cur.execute(queries.INCREMENT_COINS, (ctx.author.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="steal", help="Attempt to steal coins [3hrs]")
	async def steal_coins(self, ctx: commands.Context, target: discord.Member):
		if target.id == ctx.author.id or target.bot:
			return await ctx.send(":x:")

		elif random.randint(0, 3) != 0:
			return await ctx.send(f"**{ctx.author.display_name}** failed")

		with DBConnection() as con:
			con.cur.execute("SELECT balance FROM coins WHERE userID = %s", (ctx.author.id,))

			try:
				author_coins = con.cur.fetchone().balance
			except AttributeError:
				author_coins = 0

			con.cur.execute("SELECT balance FROM coins WHERE userID = %s", (target.id,))

			try:
				target_coins = con.cur.fetchone().balance
			except AttributeError:
				target_coins = 0

			max_coins = int(min(author_coins * 0.05, target_coins * 0.05, 1000))

			amount = random.randint(0, max(0, max_coins))

			con.cur.execute(queries.INCREMENT_COINS, (ctx.author.id, amount))
			con.cur.execute(queries.DECREMENT_COINS, (target.id, amount))

		msg = f"**{ctx.author.display_name}** stole **{amount:,}** coins from **{target.display_name}**"

		await ctx.send(msg)

	@commands.command(name="gift", help="Gift some coins")
	async def gift(self, ctx, target: discord.Member, amount: int):
		if amount <= 0 or target.id == ctx.author.id or target.bot:
			return await ctx.send(":x:")

		with DBConnection() as con:
			con.cur.execute("SELECT balance FROM coins WHERE userID = %s", (ctx.author.id,))

			try:
				author_coins = con.cur.fetchone().balance
			except AttributeError:
				author_coins = 0

			if author_coins < amount:
				await ctx.send(f":x: **{ctx.author.display_name}, you do not have enough coins to gift**")

			else:
				con.cur.execute(queries.DECREMENT_COINS, (ctx.author.id, amount))
				con.cur.execute(queries.INCREMENT_COINS, (target.id, amount))

		return await ctx.send(f"**{ctx.author.display_name}** gifted **{amount:,}** coins to **{target.display_name}**")

	@commands.is_owner()
	@commands.command(name="setcoins", hidden=True)
	async def set_coins(self, ctx, user: discord.Member, amount: int):
		with DBConnection() as con:
			con.cur.execute(queries.SET_COINS, (user.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.command(name="coinlb", aliases=["clb"], help="Show the server coin leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		lb = CoinLeaderboard()

		await ctx.send(lb.get(ctx.author))


def setup(bot):
	bot.add_cog(Bank(bot))