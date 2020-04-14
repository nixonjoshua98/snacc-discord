import random

from discord.ext import commands

from bot.common import IntegerRange
from bot.common.queries import CoinsSQL
from bot.common.database import DBConnection


class Casino(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.cooldown(25, 60 * 60 * 6, commands.BucketType.user)
	@commands.command(name="sp", help="Spin machine")
	async def spin(self, ctx):
		def get_win_bounds(amount) -> tuple:
			low = max([amount * 0.75, amount - (25 + (7.50 * amount / 1000))])
			upp = min([amount * 2.00, amount + (50 + (10.0 * amount / 1000))])
			return max(int(low), amount - 750), min(int(upp), amount + 950)

		with DBConnection() as con:
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))
			init_bal = getattr(con.cur.fetchone(), "balance", 10)
			final_bal = max(0, random.randint(*get_win_bounds(init_bal)))
			con.cur.execute(CoinsSQL.UPDATE, (ctx.author.id, final_bal))

		text = 'won' if (final_bal - init_bal) > 0 else 'lost'

		msg = f"**{ctx.author.display_name}** has {text} **{abs(final_bal - init_bal)}** coins on the spin machine."

		await ctx.send(msg)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="fl", aliases=["flip"], help="Coin flip")
	async def flip(self, ctx, amount: IntegerRange(0, 25_000) = 100):
		with DBConnection() as con:
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))
			init_bal = max(getattr(con.cur.fetchone(), "balance", 10), 10)

			if init_bal < amount:
				return await ctx.send("You do not have enough coins")

			final_bal = init_bal + amount if random.randint(0, 1) == 0 else init_bal - amount

			con.cur.execute(CoinsSQL.UPDATE, (ctx.author.id, final_bal))

		text = 'won' if final_bal > init_bal else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(amount):,}** coins by flipping a coin.")


def setup(bot):
	bot.add_cog(Casino(bot))
