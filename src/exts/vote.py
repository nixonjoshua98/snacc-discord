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
	def __init__(self, bot, token, *, autopost, webhook_path, webhook_auth, webhook_port):

		self.bot = bot
		self.token = token

		self.webhook_path = webhook_path
		self.webhook_auth = webhook_auth
		self.webhook_port = webhook_port

		if autopost:
			asyncio.create_task(self.auto_post())

		asyncio.create_task(self.webhook())

	async def auto_post(self):
		url = f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats"

		headers = {"Authorization": self.token}

		while not self.bot.is_closed():
			body = {"users": len(self.bot.users), "guilds": len(self.bot.guilds)}

			async with httpx.AsyncClient() as client:
				try:
					r = await client.post(url, headers=headers, data=body)
				except httpx.ReadTimeout:
					""" ... """
				else:
					print(r.json())

			await asyncio.sleep(1_800)

	async def webhook(self):
		async def vote_handler(request):
			req_auth = request.headers.get('Authorization')

			if self.webhook_auth == req_auth:
				data = await request.json()

				self.bot.dispatch("botlist_vote", data)

				return web.Response()

			else:
				return web.Response(status=401)

		app = web.Application(loop=self.bot.loop)

		app.router.add_post(self.webhook_path, vote_handler)

		runner = web.AppRunner(app)

		await runner.setup()

		webserver = web.TCPSite(runner, '0.0.0.0', self.webhook_port)

		await webserver.start()


class Vote(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_startup")
	async def on_startup(self):

		dbl.DBLClient(
			self.bot,
			os.environ["DBL_TOKEN"],
			autopost=True,
			webhook_port=4934,
			webhook_path="/dblwebhook",
			webhook_auth=os.environ["DBL_AUTH"]
		)

		DiscordBotList(
			self.bot,
			os.environ["BOTLIST_TOKEN"],
			autopost=True,
			webhook_port=5002,
			webhook_path="/botlistwebhook",
			webhook_auth=os.environ["BOTLIST_AUTH"],
		)

		print("Created vote clients")

	@commands.Cog.listener(name="on_dbl_test")
	async def on_dbl_test(self, data):
		print(data)

	@commands.Cog.listener("on_botlist_vote")
	async def on_botlist_vote(self, data):
		await self.on_dbl_vote(dict(user=data["id"]))

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):

		user_id = int(data["user"])

		user = self.bot.get_user(user_id)

		empire = await self.bot.db["empires"].find_one({"_id": user_id}) or dict()

		reward = int(min(50_000, max(utils.net_income(empire), 5_000) * 5))

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
