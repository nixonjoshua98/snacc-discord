import random

from discord.ext import commands
from src.structures import PlayerCoins


class CoinFlip:
	def __init__(self, ctx: commands.Context):
		self._ctx = ctx

	async def flip(self) -> int:
		coins = PlayerCoins(self._ctx.author)

		start_balance = coins.balance

		win_amount = int(min(750, coins.balance * 0.5))

		if random.randint(0, 1) == 0:
			coins.add(win_amount)

		else:
			coins.deduct(win_amount)

		return coins.balance - start_balance
