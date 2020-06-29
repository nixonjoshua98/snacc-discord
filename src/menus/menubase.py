import discord
import asyncio

from typing import Union

from discord.ext import commands


class MenuBase:
	def __init__(self, bot: commands.Bot, **options):
		self._bot = bot

		self._message = None
		self._buttons = dict()
		self._destination = None

		self._timeout = options.get("timeout")

	async def on_reaction_add(self, react: discord.Reaction):
		callback = self._buttons.get(str(react.emoji))

		if callback is not None:
			await callback()

	async def send_initial_message(self, destination: discord.abc.Messageable) -> discord.Message: ...

	async def update_message(self): ...

	async def send(self, destination: discord.abc.Messageable):
		self._message = await self.send_initial_message(destination)

		await self._add_reactions()

		self._destination = destination

		def wait_for(react_, user_):
			return self.can_user_interact(user_) and react_.message.id == self._message.id

		while True:
			try:
				react, user = await self._bot.wait_for("reaction_add", timeout=self._timeout, check=wait_for)

			except asyncio.TimeoutError:
				return await self.after_menu_expire()

			else:
				await self.on_reaction_add(react)

				await self._remove_react(react, user)

				await self.update_message()

	async def after_menu_expire(self):
		try:
			await self._message.clear_reactions()

		except (discord.HTTPException, discord.Forbidden):
			pass

	def add_button(self, emoji, callback):
		self._buttons[emoji] = callback

	def can_user_interact(self, user: Union[discord.User, discord.Member]):
		if isinstance(self._destination, commands.Context):
			return self._destination.author.id == user.id

		elif isinstance(self._destination, (discord.User, discord.Member)):
			return self._destination.id == user.id

	async def _add_reactions(self):
		for emoji in self._buttons:
			await self._message.add_reaction(emoji)

	async def _remove_react(self, react, user):
		try:
			await react.remove(user)

		except (discord.Forbidden, discord.HTTPException):
			""" Failed. """

	async def _clear_reactions(self):
		await self._message.clear_reactions()
