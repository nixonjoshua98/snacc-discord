import httpx
import discord
import asyncio

from discord.ext import commands, tasks

import matplotlib.pyplot as plt
import datetime as dt


class SnaccCoin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._price_cache = dict()

		self.start_price_update_loop()

	async def cog_before_invoke(self, ctx):
		if self._price_cache.get("history", None) is None:
			await self.update_prices()

	@commands.group(name="sc", invoke_without_command=True)
	async def snacc_coin_group(self, ctx):
		""" Show the Snacc Coin history and current price. """

		file_name = self.create_graph(self._price_cache["history"])

		embed = discord.Embed(title="Snacc Coin History", color=discord.Color.orange())

		embed.description = f":moneybag: **Current Price: ${self._price_cache['current']:,}**"

		file = discord.File(file_name, filename=file_name)

		embed.set_image(url=f"attachment://{file_name}")

		await ctx.send(file=file, embed=embed)


	@staticmethod
	async def get_history():
		date_end = dt.datetime.utcnow()
		date_start = date_end - dt.timedelta(days=31)

		async with httpx.AsyncClient() as client:
			r = await client.get(
				f"https://api.coindesk.com/v1/bpi/historical/close.json?"
				f"start={date_start.strftime('%Y-%m-%d')}&end={date_end.strftime('%Y-%m-%d')}"
			)

			data = r.json()

		return {k: int(v) for k, v in data["bpi"].items()}

	@staticmethod
	async def get_current():
		async with httpx.AsyncClient() as client:
			r = await client.get(f"https://api.coindesk.com/v1/bpi/currentprice.json")

			data = r.json()

		return int(data["bpi"]["USD"]["rate_float"])

	@staticmethod
	def create_graph(data):
		fig, ax = plt.subplots(facecolor="#2f3136")

		plt.plot(data.keys(), data.values(), linewidth=3, color="white")

		plt.gca().axes.get_xaxis().set_ticks([])

		ax.tick_params(axis='y', colors='white')

		plt.grid(True)

		plt.savefig('graph.png', facecolor=fig.get_facecolor(), transparent=True)

		return "graph.png"

	def start_price_update_loop(self):
		async def predicate():
			print("Starting loop: Snacc Coin")

			self.update_prices_loop.start()

		asyncio.create_task(predicate())

	@tasks.loop(minutes=15.0)
	async def update_prices_loop(self):
		await self.update_prices()

	async def update_prices(self):
		self._price_cache["current"] = await self.get_current()
		self._price_cache["history"] = await self.get_history()

		self._price_cache["history"]["current"] = self._price_cache["current"]


def setup(bot):
	bot.add_cog(SnaccCoin(bot))
