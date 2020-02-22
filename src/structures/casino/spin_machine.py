import asyncio
import random

from num2words import num2words

from discord.ext import commands
from src.structures import PlayerCoins


class SpinMachine:
	def __init__(self, ctx: commands.Context):
		self._ctx = ctx

	@staticmethod
	def get_win_bounds(amount) -> tuple:
		lower = int(max(amount * 0.75, amount - (25 + (5.0 * amount / 1000))))
		upper = int(min(amount * 1.50, amount + (35 + (10.0 * amount / 1000))))

		return lower, upper

	async def spin(self) -> int:
		def num2emoji(num):
			return "".join([f":{num2words(digit)}:" for digit in f"{num:05d}"])

		coins = PlayerCoins(self._ctx.author)

		bet_amount = coins.balance

		coins.deduct(bet_amount)

		lower, upper = self.get_win_bounds(bet_amount)

		# Add winnings before the actual spin to avoid issues
		winnings = max(0, random.randint(lower, upper))
		winnings = winnings + 2 if winnings == bet_amount else winnings

		coins.add(winnings)

		message = await self._ctx.send(f":arrow_right:{num2emoji(bet_amount)}:arrow_left:")

		for i in range(2):
			await asyncio.sleep(1.0)

			temp_num = max(0, random.randint(lower, upper))

			# Stops the number being the bet amount (looks weird)
			temp_num = temp_num + 1 if temp_num == bet_amount else temp_num

			await message.edit(content=f":arrow_right:{num2emoji(temp_num)}:arrow_left:")

		await asyncio.sleep(1.0)
		await message.edit(content=f":arrow_right:{num2emoji(winnings)}:arrow_left:")
		return winnings - bet_amount
