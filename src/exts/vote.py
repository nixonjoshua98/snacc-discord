import dbl
import os
import discord
import asyncio

from aiohttp import web

from discord.ext import commands

from src import utils

from src.common import SupportServer


class DiscordBotList:
	def __init__(self, bot):
		self.bot = bot

		asyncio.create_task(self.webhook())

	async def webhook(self):
		async def vote_handler(request):
			print(request)

		app = web.Application(loop=self.bot.loop)

		app.router.add_post("/discordbotlistwebhook", vote_handler)

		runner = web.AppRunner(app)

		await runner.setup()

		webserver = web.TCPSite(runner, '0.0.0.0', 5000)

		await webserver.start()


class Vote(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.dbl = None

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if (token := os.getenv("DBL_TOKEN")) not in (None, "TOKEN", "VALUE", "", " "):
			dbl.DBLClient(self.bot, token, autopost=True, webhook_auth='snacc')

			DiscordBotList(self.bot)

			print("Created DBL client")

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		user_id = int(data["user"])

		user = self.bot.get_user(user_id)

		empire = await self.bot.db["empires"].find_one({"_id": user_id}) or dict()

		multiplier = 1.25 if data["isWeekend"] else 1.0

		reward = int(min(50_000, max(utils.net_income(empire) * 5, 5_000)) * multiplier)

		await self.bot.db["bank"].update_one({"_id": user_id}, {"$inc": {"usd": reward}}, upsert=True)

		if user is not None:
			support_server = self.bot.get_guild(SupportServer.ID)

			try:
				await user.send(f"Thank you for voting for me! You have received **${reward:,}** :heart:")

				member = support_server.get_member(user_id)

				if member is None:
					await user.send(f"psst...you can join our support server here {SupportServer.LINK}")

			except (discord.Forbidden, discord.HTTPException):
				""" Failed """


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
