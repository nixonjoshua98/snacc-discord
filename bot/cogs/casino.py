import random

from discord.ext import commands

from bot.common.converters import Clamp


class Casino(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.bank = self.bot.get_cog("Bank")

	async def cog_before_invoke(self, ctx):
		self.bank = self.bot.get_cog("Bank") if self.bank is None else self.bank

		ctx.user_balance = await self.bank.get_user_balances(ctx.author)

	@commands.cooldown(25, 60 * 60 * 3, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Spin machine")
	async def spin(self, ctx):
		""" Use a spin machine. Limited to 25 spins every 3 hours """
		def get_winning(amount) -> int:
			low, high = max(amount * -0.75, -750), min(amount * 2.0, 1000)

			return random.randint(int(low), int(high))

		bal_diff = get_winning(ctx.user_balance["coins"])

		await self.bank.update_coins(ctx.author, bal_diff)

		text = 'won' if bal_diff > 0 else 'lost'

		msg = f"**{ctx.author.display_name}** has {text} **{abs(bal_diff)}** coins on the spin machine."

		await ctx.send(msg)

	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.command(name="fl", aliases=["flip"], usage="<bet=100>")
	async def flip(self, ctx, amount: Clamp(1, 5_000) = 100):
		""" Flip a coin """

		if ctx.user_balance["coins"] < amount:
			return await ctx.send("You do not have enough coins. Lower your bet.")

		bal_diff = amount if random.randint(0, 1) == 0 else amount * -1

		await self.bank.update_coins(ctx.author, bal_diff)

		text = 'won' if bal_diff > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(amount):,}** coins by flipping a coin.")


def setup(bot):
	bot.add_cog(Casino(bot))
