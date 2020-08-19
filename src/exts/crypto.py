import httpx
import discord
import asyncio

from discord.ext import commands, tasks

import matplotlib.pyplot as plt
import datetime as dt

from src.common.converters import Range


class Crypto(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._price_cache = dict()

		if not self.bot.debug:
			print("Starting loop: Crpyto")

			self.update_prices_loop.start()

	async def cog_before_invoke(self, ctx):
		if self._price_cache.get("history") is None:
			await self.update_prices()

	@commands.group(name="crpto", aliases=["c"], invoke_without_command=True)
	async def crypto_group(self, ctx):
		""" Show the current price of Bitcoin. """

		current_price = self._price_cache['current']

		embed = ctx.bot.embed(title="Cryptocurrency", description=f":moneybag: **Current Price: ${current_price:,}**")

		file = discord.File("graph.png", filename="graph.png")

		embed.set_image(url="attachment://graph.png")
		embed.set_footer(text="Powered by CoinDesk")

		await ctx.send(file=file, embed=embed)

	@crypto_group.command(name="buy")
	async def buy_coin(self, ctx, amount: Range(1, 100)):
		""" Buy Bitcoin(s). """

		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		price = self._price_cache["current"] * amount

		if price > bank.get("usd", 0):
			await ctx.send(f"You can't afford to buy **{amount}** Bitcoin(s).")

		else:
			await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"btc": amount})
			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": price})

			await ctx.send(f"You bought **{amount}** Bitcoin(s) for **${price:,}**!")

	@crypto_group.command(name="sell")
	async def sell_coin(self, ctx, amount: Range(1, 100)):
		""" Sell Bitcoin(s). """

		price = self._price_cache["current"] * amount

		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		if amount > bank.get("btc", 0):
			await ctx.send(f"You are trying to sell more Bitcoin than you currently own.")

		else:
			await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": price})
			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"btc": amount})

			await ctx.send(f"You sold **{amount}** Bitcoin(s) for **${price:,}**!")

	@staticmethod
	async def get_history():
		date_end = dt.datetime.utcnow()
		date_start = date_end - dt.timedelta(days=31)

		async with httpx.AsyncClient() as client:
			r = await client.get(
				f"https://api.coindesk.com/v1/bpi/historical/close.json?"
				f"start={date_start.strftime('%Y-%m-%d')}&"
				f"end={date_end.strftime('%Y-%m-%d')}"
			)

			data = r.json()

		return {k: int(v) for k, v in data["bpi"].items()}

	@staticmethod
	async def get_current():
		async with httpx.AsyncClient() as client:
			r = await client.get(f"https://api.coindesk.com/v1/bpi/currentprice.json")

			data = r.json()

		return int(data["bpi"]["USD"]["rate_float"])

	def create_graph(self):
		data = self._price_cache["history"]

		fig, ax = plt.subplots(facecolor="#2f3136")

		plt.plot(data.keys(), data.values(), linewidth=3, color="white")

		plt.gca().axes.get_xaxis().set_ticks([])

		ax.tick_params(axis='y', colors='white')

		plt.grid(True)

		plt.savefig('graph.png', facecolor=fig.get_facecolor(), transparent=True)

	@tasks.loop(minutes=5.0)
	async def update_prices_loop(self):
		await self.update_prices()

	async def update_prices(self):
		self._price_cache["current"] = await self.get_current()
		self._price_cache["history"] = await self.get_history()

		self._price_cache["history"]["current"] = self._price_cache["current"]

		self.create_graph()


def setup(bot):
	bot.add_cog(Crypto(bot))
