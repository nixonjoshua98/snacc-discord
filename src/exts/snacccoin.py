import asyncio

from discord.ext import commands, tasks


class SnaccCoin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.start_snacc_coin_loop()

	@commands.group(name="sc", invoke_without_command=True)
	async def snacc_coin_group(self, ctx):
		""" Show the current price of the Snacc Coin. """

	@staticmethod
	async def get_new_snacc_coin():
		return {"price": 0, "date_updated": 0}

	def start_snacc_coin_loop(self):
		async def predicate():
			if not self.bot.debug and await self.bot.is_snacc_owner():
				print("Starting loop: Snacc Coin")

				await asyncio.sleep(60 * 25)

				self.snacc_coin_loop.start()

		asyncio.create_task(predicate())

	@tasks.loop(minutes=25)
	async def snacc_coin_loop(self):
		coin = await self.get_new_snacc_coin()

		print(coin)


def setup(bot):
	bot.add_cog(SnaccCoin(bot))
