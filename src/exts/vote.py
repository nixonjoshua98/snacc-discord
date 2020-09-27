import dbl
import os
import httpx
import discord
import asyncio

from aiohttp import web

from discord.ext import commands

from src import utils

from src.common import SupportServer


class DiscordBotList:
	def __init__(self, bot, *, webhook_path, webhook_auth, webhook_port):
		self.bot = bot

		self.webhook_path = webhook_path
		self.webhook_auth = webhook_auth
		self.webhook_port = webhook_port

		asyncio.create_task(self.webhook())

		asyncio.create_task(self.auto_post())

	async def webhook(self):
		async def vote_handler(request):
			print(request)

		app = web.Application(loop=self.bot.loop)

		app.router.add_post(self.webhook_path, vote_handler)

		runner = web.AppRunner(app)

		await runner.setup()

		webserver = web.TCPSite(runner, '0.0.0.0', self.webhook_port)

		await webserver.start()

	async def auto_post(self):
		url = f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats"

		headers = {"Authorization": self.webhook_auth}

		while not self.bot.is_closed():
			body = {"users": len(self.bot.users), "guilds": len(self.bot.guilds)}

			async with httpx.AsyncClient() as client:
				r = await client.post(url, headers=headers, data=body)

			await asyncio.sleep(1_800)


class Vote(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if (token := os.getenv("DBL_TOKEN")) not in (None, "TOKEN", "VALUE", "", " "):
			auth = os.environ["VOTE_AUTH"]

			dbl.DBLClient(
				self.bot,
				token,
				autopost=True,
				webhook_port=4999,
				webhook_path="/topgghook",
				webhook_auth=auth
			)

			DiscordBotList(self.bot, webhook_path="/dblhook", webhook_auth=auth, webhook_port=5001)

			print("Created vote clients")

	@commands.Cog.listener(name="on_dbl_test")
	async def on_dbl_test(self, data):
		print(data)

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
