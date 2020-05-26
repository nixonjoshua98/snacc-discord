import asyncio

import discord
from discord.ext import commands

from snacc.common.emoji import Emoji


class MenuBase:
	def __init__(self, pages: list, timeout: int):
		self.bot = None
		self.ctx = None
		self.message = None

		self.current_page = 0

		self.timeout = timeout
		self.pages = pages

		self._buttons = dict()

		self.add_buttons()

	def add_buttons(self): ...

	async def send_initial_message(self) -> discord.Message:
		page = self.pages[0]

		if isinstance(page, discord.Embed):
			return await self.ctx.send(embed=page)

		return await self.ctx.send(content=page)

	async def update(self):
		page = self.pages[self.current_page]

		if isinstance(page, discord.Embed):
			return await self.message.edit(embed=page)

		return await self.message.edit(content=page)

	def add_button(self, emoji, callback):
		self._buttons[emoji] = callback

	async def send(self, ctx: commands.Context):
		self.ctx, self.bot = ctx, ctx.bot

		self.message = await self.send_initial_message()

		await self._add_reactions()

		def wait_for(react_, user_):
			return user_.id == ctx.author.id and react_.message.id == self.message.id

		while True:
			try:
				react, user = await self.bot.wait_for("reaction_add", timeout=self.timeout, check=wait_for)

			except asyncio.TimeoutError:
				try:
					await self.message.clear_reactions()

					await self.message.delete()

				except (discord.Forbidden, discord.HTTPException):
					""" Failed """

				break

			else:
				callback = self._buttons.get(str(react.emoji), None)

				if callback is not None:
					await callback()

				await self._after_callback(react, user)

				await self.update()

	async def _add_reactions(self):
		for emoji in self._buttons:
			await self.message.add_reaction(emoji)

	async def _after_callback(self, react, user):
		try:
			await react.remove(user)

		except (discord.Forbidden, discord.HTTPException):
			""" Failed """


class Menu(MenuBase):
	def __init__(self, pages: list, *, timeout: int = None):
		super(Menu, self).__init__(pages, timeout)

	def add_buttons(self):
		if len(self.pages) > 1:
			self.add_button(Emoji.REWIND, self.on_rewind)
			self.add_button(Emoji.ARROW_LEFT, self.on_arrow_left)
			self.add_button(Emoji.ARROW_RIGHT, self.on_arrow_right)
			self.add_button(Emoji.FAST_FORWARD, self.on_fast_forward)

	async def on_rewind(self):
		self.current_page = 0

	async def on_arrow_left(self):
		self.current_page = max(0, self.current_page - 1)

	async def on_arrow_right(self):
		self.current_page = min(len(self.pages) - 1, self.current_page + 1)

	async def on_fast_forward(self):
		self.current_page = len(self.pages) - 1
