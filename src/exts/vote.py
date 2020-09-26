import dbl
import os
import discord

from discord.ext import commands

from src.common import SupportServer

from aiohttp import web


async def webhook(self):
	async def vote_handler(request):
		print(request)

		req_auth = request.headers.get('Authorization')
		if self.webhook_auth == req_auth:
			data = await request.json()
			if data.get('type') == 'upvote':
				event_name = 'dbl_vote'
			elif data.get('type') == 'test':
				event_name = 'dbl_test'
			self.bot.dispatch(event_name, data)
			return web.Response()
		else:
			return web.Response(status=401)

	app = web.Application(loop=self.loop)
	app.router.add_post(self.webhook_path, vote_handler)
	runner = web.AppRunner(app)
	await runner.setup()
	self._webserver = web.TCPSite(runner, '0.0.0.0', self.webhook_port)
	await self._webserver.start()


class Vote(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

		self.dbl = None

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if (token := os.getenv("DBL_TOKEN")) not in (None, "TOKEN", "VALUE", "", " "):
			dbl.DBLClient.webhook = webhook

			self.dbl = dbl.DBLClient(self.bot, token, autopost=True, port=10010, webhook_auth="snacc")

			print("Created DBL webhook")

	@commands.Cog.listener("on_dbl_test")
	async def on_dbl_test(self, data):
		print(data)

	@commands.Cog.listener(name="on_dbl_vote")
	async def on_dbl_vote(self, data):
		user_id = data["user"]

		user = self.bot.get_user(user_id)

		if user is not None:
			support_server = self.bot.get_guild(SupportServer.ID)

			try:
				await user.send("Thank you for voting for me! :heart:")

				member = support_server.get_member(user_id)

				if member is None:
					await user.send(f"psst...you can join our support server here {SupportServer.LINK}")

			except (discord.Forbidden, discord.HTTPException):
				""" Failed """


def setup(bot):
	if not bot.debug:
		bot.add_cog(Vote(bot))
