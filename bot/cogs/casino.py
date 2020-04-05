import random

from num2words import num2words

from discord.ext import commands

from bot.common import checks, ChannelTags
from bot.common.queries import CoinsSQL
from bot.common.database import DBConnection


class Casino(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return checks.channel_has_tag(ctx, ChannelTags.GAME)

	@commands.cooldown(25, 60 * 60 * 6, commands.BucketType.user)
	@commands.command(name="sp", help="Spin machine")
	async def spin(self, ctx):
		def get_win_bounds(amount) -> tuple:
			low = max([amount * 0.75, amount - (25 + (7.50 * amount / 1000))])
			upp = min([amount * 2.00, amount + (50 + (10.0 * amount / 1000))])
			return int(low), int(upp)

		with DBConnection() as con:
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))
			initial = con.cur.fetchone()
			init_bal = max(getattr(initial, "balance", 10), 10)

			lower, upper = get_win_bounds(init_bal)
			final_bal = max(0, random.randint(lower, upper))

			con.cur.execute(CoinsSQL.UPDATE, (ctx.author.id, final_bal))

		bal_change = final_bal - init_bal
		text = 'won' if bal_change > 0 else 'lost'

		msg = f":arrow_right:{''.join([f':{num2words(digit)}:' for digit in f'{final_bal:05d}'])}:arrow_left:\n" \
			  f"**{ctx.author.display_name}** has {text} **{abs(bal_change)}** coins!"

		await ctx.send(msg)

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="fl", help="Coin flip")
	async def flip(self, ctx):
		with DBConnection() as con:
			con.cur.execute(CoinsSQL.SELECT_USER, (ctx.author.id,))

			initial = con.cur.fetchone()

			init_bal = max(getattr(initial, "balance", 10), 10)

			amount = int(min(5000, init_bal // 2))

			final_bal = init_bal + amount if random.randint(0, 1) == 0 else init_bal - amount

			con.cur.execute(CoinsSQL.UPDATE, (ctx.author.id, final_bal))

		text = 'won' if final_bal > init_bal else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(amount):,}** coins by flipping a coin")


def setup(bot):
	bot.add_cog(Casino(bot))
