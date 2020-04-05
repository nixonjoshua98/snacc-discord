import random

from discord.ext import commands

from bot.common import checks, CoinsSQL, ChannelTags

from bot.common.converters import NotAuthorOrBot, IntegerRange

from bot.common.database import DBConnection

from bot.structures import CoinLeaderboard


class Bank(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.leaderboards = dict()

	async def cog_check(self, ctx):
		return checks.channel_has_tag(ctx, ChannelTags.CASINO)

	@commands.command(name="bal", help="Coin balance")
	async def balance(self, ctx: commands.Context):
		with DBConnection() as con:
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))

			user = con.cur.fetchone()

		balance = user.balance if user is not None else 0

		await ctx.send(f":moneybag: **{ctx.author.display_name}** has a total of **{balance:,}** coins")

	@commands.cooldown(1, 60 * 15, commands.BucketType.user)
	@commands.command(name="free", aliases=["pickup"], help="Free coins!")
	async def free(self, ctx: commands.Context):
		amount = random.randint(15, 50)

		with DBConnection() as con:
			con.cur.execute(CoinsSQL.INCREMENT, (ctx.author.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="steal", usage="<user>")
	async def steal_coins(self, ctx: commands.Context, target: NotAuthorOrBot()):
		if random.randint(0, 2) != 0:
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

	@commands.command(name="gift", usage="<user> <amount>")
	async def gift(self, ctx, target: NotAuthorOrBot(), amount: IntegerRange(1, 10000)):
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
	@commands.command(name="sc", help="Set user coins")
	async def set_coins(self, ctx, user: NotAuthorOrBot(), amount: IntegerRange(0, 1_000_000)):
		with DBConnection() as con:
			con.cur.execute(CoinsSQL.UPDATE, (user.id, amount))

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.command(name="clb", help="Leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		if self.leaderboards.get(ctx.guild.id, None) is None:
			self.leaderboards[ctx.guild.id] = CoinLeaderboard(ctx.guild, self.bot)

		lb = self.leaderboards[ctx.guild.id]

		return await ctx.send(lb.get(ctx.author))


def setup(bot):
	bot.add_cog(Bank(bot))