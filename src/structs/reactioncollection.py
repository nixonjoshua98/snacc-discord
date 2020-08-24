import time
import discord
import asyncio

from src.common.emoji import Emoji


async def run_coro(coro):
	try:
		await coro
	except (discord.Forbidden, discord.HTTPException):
		""" Failed. """


class ReactionCollection:
	def __init__(self, bot, msg, react=Emoji.CHECK_MARK, **kwargs):

		self.bot = bot
		self.msg = msg
		self.react = react

		self.duration = kwargs.get("duration", 60.0)
		self.max_reacts = kwargs.get("max_reacts", 100)
		self.delete_after = kwargs.get("delete_after", True)

		self.message: discord.Message = None

		self._running = True

		self.members = set()

	@classmethod
	async def from_existing(cls, bot, msg, chnl_id, msg_id, react=Emoji.CHECK_MARK, **kwargs):
		inst = cls(bot, msg, react=react, **kwargs)

		chnl = bot.get_channel(chnl_id)

		if chnl is None:
			return None

		message = await chnl.fetch_message(msg_id)

		if message is None:
			return None

		inst.message = message

		for react in message.reactions:
			if react.emoji == react:
				inst.members = await react.users().flatten()
				break

		return inst

	async def send_initial_message(self, destination):
		if isinstance(self.msg, str):
			return await destination.send(self.msg)

		elif isinstance(self.msg, discord.Embed):
			return await destination.send(embed=self.msg)

	async def on_react(self, _, user):
		self.members.add(user)

		if self.max_reacts is not None and len(self.members) >= self.max_reacts:
			self._running = False

	async def on_end(self):
		if self.delete_after:
			return await run_coro(self.message.delete())

	async def _add_reactions(self):
		await self.message.add_reaction(self.react)

	async def _loop(self):
		def wait_for(r, u):
			return not u.bot and r.message.id == self.message.id and r.emoji == self.react and u not in self.members

		start = time.time()

		timeout = self.duration

		while self._running:
			try:
				react, user = await self.bot.wait_for("reaction_add", timeout=timeout, check=wait_for)

			except asyncio.TimeoutError:
				return await self.on_end()

			else:
				if react.emoji == self.react:
					await self.on_react(react, user)

			# - Update timeout
			timeout -= time.time() - start

			start = time.time()

		return await self.on_end()

	async def prompt(self, destination):
		self.message = await self.send_initial_message(destination)

		await self._add_reactions()

		await self._loop()

		return list(self.members)

