import asyncio
import discord

import datetime as dt

from src.common.emoji import Emoji


class ReactionCollection:
	def __init__(self, bot, msg, react=Emoji.TADA, **kwargs):

		self.bot = bot
		self.msg = msg
		self.react = react

		self.duration = kwargs.get("duration", 60.0)
		self.max_reacts = kwargs.get("max_reacts", 100)
		self.delete_after = kwargs.get("delete_after", True)

		self.message: discord.Message = None

		self._running = True

		self.members = set()

	async def get_users(self):
		self.message = await self.message.channel.fetch_message(self.message.id)

		for react in self.message.reactions:
			if react.emoji == self.react:
				return [u for u in await react.users().flatten() if not u.bot and isinstance(u, discord.Member)]

		return []

	async def send_initial_message(self, destination):
		if isinstance(self.msg, str):
			return await destination.send(self.msg)

		elif isinstance(self.msg, discord.Embed):
			return await destination.send(embed=self.msg)

	async def on_react(self, _, user):
		self.members.add(user)

		if self.max_reacts is not None and len(self.members) >= self.max_reacts:
			self._running = False

	async def _loop(self, destination):
		self.message = await self.send_initial_message(destination)

		await self.message.add_reaction(self.react)

		now = dt.datetime.utcnow()

		end = now + dt.timedelta(seconds=self.duration)

		seconds = (end - now).total_seconds()

		await asyncio.sleep(seconds)

	async def prompt(self, destination):
		await self._loop(destination)

		users = await self.get_users()

		if self.delete_after:
			return await self.message.delete()

		return users

