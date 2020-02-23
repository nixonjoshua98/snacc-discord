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
		upper = min(amount * 1.50, amount + (35 + (7.5 * amount / 1000)))
		lower = max(amount * 0.75, amount + (upper - amount) * -0.9)

		return int(lower), int(upper)

	@staticmethod
	def create_message(amount):
		number_emoji = "".join([f":{num2words(digit)}:" for digit in f"{amount:05d}"])

		return f":arrow_right:{number_emoji}:arrow_left:\n"

	async def spin(self) -> int:
		coins = PlayerCoins(self._ctx.author)

		bet_amount = coins.balance

		coins.deduct(bet_amount)

		lower, upper = self.get_win_bounds(bet_amount)

		# Add winnings before the actual spin to avoid issues
		winnings = max(0, random.randint(lower, upper))
		winnings = winnings + 2 if winnings == bet_amount else winnings

		coins.add(winnings)

		# print(f"{lower}({lower-bet_amount}), {bet_amount}, {upper}({upper-bet_amount}), {winnings}({winnings-bet_amount})")

		message = await self._ctx.send(self.create_message(bet_amount))

		for i in range(2):
			await asyncio.sleep(1.0)

			temp_num = max(0, random.randint(lower, upper))

			# Stops the number being the bet amount (looks weird)
			temp_num = temp_num + 1 if temp_num == bet_amount else temp_num

			await message.edit(content=self.create_message(temp_num))

		await asyncio.sleep(1.0)
		await message.edit(content=self.create_message(winnings))

		return winnings - bet_amount
