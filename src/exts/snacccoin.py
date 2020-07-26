import os
import httpx
import asyncio

import datetime as dt

from discord.ext import commands, tasks

from src.common.models import SnaccCoinM


class SnaccCoin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.start_snacc_coin_loop()

	@staticmethod
	async def get_new_snacc_coin():
		def get(d, **kwargs):
			for row in d:
				if all(row.get(k, "__None__") == v for k, v in kwargs.items()):
					return row
			return None

		url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

		async with httpx.AsyncClient() as client:
			r = await client.get(url, headers={"X-CMC_PRO_API_KEY": os.getenv("CMC_PRO_API_KEY")})

		if r.status_code != httpx.codes.OK:
			return None

		data = r.json()

		btc, eth = get(data["data"], symbol="BTC"), get(data["data"], symbol="ETH")

		btc_price, eth_price = btc["quote"]["USD"]["price"], eth["quote"]["USD"]["price"]

		sc_price = (btc_price + eth_price) // 2

		sc_last_updated = dt.datetime.strptime(btc["last_updated"].replace("Z", ""), '%Y-%m-%dT%H:%M:%S.%f')

		return {"price": sc_price, "date_updated": sc_last_updated}

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

		if coin is None:
			return None

		await self.bot.execute(SnaccCoinM.INSERT_ROW, coin["price"], coin["date_updated"])


def setup(bot):
	if os.getenv("CMC_PRO_API_KEY") is not None:
		bot.add_cog(SnaccCoin(bot))

	else:
		print(f"Missing env key: CMC_PRO_API_KEY")
