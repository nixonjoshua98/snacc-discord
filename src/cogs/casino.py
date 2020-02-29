from discord.ext import commands

from src.common import checks

from src.structures.casino import SpinMachine
from src.structures.casino import CoinFlip


class Casino(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx) and commands.guild_only()

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(25, 60 * 60 * 24, commands.BucketType.user)
	@commands.command(name="spin", aliases=["sp"], help="Slot machine [LOW RISK]")
	async def spin(self, ctx):
		machine = SpinMachine(ctx)

		winnings = await machine.spin()

		text = 'won' if winnings > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings):,}** coins!")

	@checks.has_minimum_coins("coins.json", 10)
	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="flip", aliases=["fl"], help="Flip a coin [HIGH RISK]")
	async def flip(self, ctx):
		coin = CoinFlip(ctx)

		winnings = await coin.flip()

		text = 'won' if winnings > 0 else 'lost'

		await ctx.send(f"**{ctx.author.display_name}** has {text} **{abs(winnings):,}** coins by flipping a coin!")

