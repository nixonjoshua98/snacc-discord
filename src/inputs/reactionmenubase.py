import inspect
import asyncio
import discord

from .inputbase import InputBase

from typing import Callable
from dataclasses import dataclass


def button(emoji, **options):
	def decorator(func):
		func.__menu_button__ = emoji
		func.__menu_button_options__ = options

		return func

	return decorator


@dataclass(frozen=True)
class Button:
	emoji: str
	callback: Callable
	index: int


class ReactionMenuBase(InputBase):
	def __init__(self, bot, author, **kwargs):
		super().__init__(bot, author, **kwargs)

		self._buttons = self.get_buttons()

	def wait_for(self, react, user):
		return react.message.id == self.message.id and (self.author is None or user.id == self.author.id)

	async def on_update(self): ...

	async def on_timeout(self):
		await self.clear_reactions()

	async def on_exit(self):
		await self.clear_reactions()

	async def send(self, destination):
		await super().send(destination)

		await self.add_reactions()

		while True:
			try:
				react, user = await self.bot.wait_for("reaction_add", timeout=self.timeout, check=self.wait_for)

			except asyncio.TimeoutError:
				return await self.on_timeout()

			else:
				btn = discord.utils.get(self._buttons, emoji=str(react.emoji))

				await self.remove_reaction(react, user)

				if btn is not None:
					await btn.callback()

				await self.on_update()

				if self.is_ended:
					return await self.on_exit()

	def get_buttons(self) -> list:
		methods = inspect.getmembers(self, lambda a: not (inspect.isfunction(a)))

		buttons = []

		for name, inst in methods:
			if hasattr(inst, "__menu_button__") and hasattr(inst, "__menu_button_options__"):
				index = inst.__menu_button_options__.get("index", 0)

				btn = Button(inst.__menu_button__, getattr(self, name), index)

				buttons.append(btn)

		return sorted(buttons, key=lambda b: b.index)

	async def add_reactions(self):
		for btn in self._buttons:
			await self.message.add_reaction(btn.emoji)

	def add_button(self, emoji, callback, index):
		btn = Button(emoji, callback, index)

		self._buttons.append(btn)

		self._buttons.sort(key=lambda b: b.index)

