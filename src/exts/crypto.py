import httpx
import discord
import asyncio

from discord.ext import commands, tasks

import matplotlib.pyplot as plt
import datetime as dt

from src.common.models import BankM
from src.common.converters import Range


class Crypto(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._price_cache = dict()

		self.start_price_update_loop()

	async def cog_before_invoke(self, ctx):
		if self._price_cache.get("history", None) is None:
			await self.update_prices()

	@commands.group(name="crpto", aliases=["c", "cry"], invoke_without_command=True)
	async def snacc_coin_group(self, ctx):
		""" Show the history of the avilable coins. """

		embed = discord.Embed(title="Cryptocurrency", color=discord.Color.orange())

		price = self._price_cache['current']

		embed.description = f":moneybag: **Current Price: ${price:,}**"

		file = discord.File("graph.png", filename="graph.png")

		embed.set_image(url="attachment://graph.png")
		embed.set_footer(text="Powered by CoinDesk")

		await ctx.send(file=file, embed=embed)

	@snacc_coin_group.command(name="buy")
	async def buy_coin(self, ctx, amount: Range(1, 100)):
		""" Buy Crpyto coins """

		async with ctx.bot.pool.acquire() as con:
			row = await BankM.get_row(con, ctx.author.id)

			price = self._price_cache["current"] * amount

			if price > row["money"]:
				await ctx.send(f"You can't afford to buy **{amount}** Bitcoin(s).")

			else:
				await con.execute(BankM.SUB_MONEY, ctx.author.id, price)
				await con.execute(BankM.ADD_BTC, ctx.author.id, amount)

				await ctx.send(f"You bought **{amount}** Bitcoin(s) for **${price:,}**!")

	@snacc_coin_group.command(name="sell")
	async def sell_coin(self, ctx, amount: Range(1, 100)):
		""" Sell Bitcoin(s). """

		async with ctx.bot.pool.acquire() as con:
			row = await BankM.get_row(con, ctx.author.id)

			price = self._price_cache["current"] * amount

			if amount > row["btc"]:
				await ctx.send(f"You are trying to sell more Bitcoin than you currently own.")

			else:
				await con.execute(BankM.ADD_MONEY, ctx.author.id, price)
				await con.execute(BankM.SUB_BTC, ctx.author.id, amount)

				await ctx.send(f"You sold **{amount}** Bitcoin(s) for **${price:,}**!")

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

		return {k: int(v // 5) for k, v in data["bpi"].items()}

	@staticmethod
	async def get_current():
		async with httpx.AsyncClient() as client:
			r = await client.get(f"https://api.coindesk.com/v1/bpi/currentprice.json")

			data = r.json()

		return int(data["bpi"]["USD"]["rate_float"]) // 5

	@staticmethod
	def create_graph(data):
		fig, ax = plt.subplots(facecolor="#2f3136")

		plt.plot(data.keys(), data.values(), linewidth=3, color="white")

		plt.gca().axes.get_xaxis().set_ticks([])

		ax.tick_params(axis='y', colors='white')

		plt.grid(True)

		plt.savefig('graph.png', facecolor=fig.get_facecolor(), transparent=True)

	def start_price_update_loop(self):
		async def predicate():
			print("Starting loop: Crpyto")

			self.update_prices_loop.start()

		asyncio.create_task(predicate())

	@tasks.loop(minutes=15.0)
	async def update_prices_loop(self):
		await self.update_prices()

	async def update_prices(self):
		self._price_cache["current"] = await self.get_current()
		self._price_cache["history"] = await self.get_history()

		self._price_cache["history"]["current"] = self._price_cache["current"]

		self.create_graph(self._price_cache["history"])


def setup(bot):
	bot.add_cog(Crypto(bot))
