import discord
import asyncio
from discord.ext import commands

from snacc.common.emoji import UEmoji


class MenuBase:
	def __init__(self):
		self.bot = None
		self.ctx = None
		self.message = None

		self._buttons = dict()

	async def send_initial_message(self) -> discord.Message:
		raise NotImplemented()

	async def update(self):
		raise NotImplemented()

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
				react, user = await self.bot.wait_for("reaction_add", timeout=60, check=wait_for)

			except asyncio.TimeoutError:
				try:
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


class EmbedMenu(MenuBase):
	def __init__(self, embeds: list, *, start_page: int = 0):
		super(EmbedMenu, self).__init__()

		self._start_page = start_page

		self.embeds = embeds
		self.current_page = 0

		self.add_button(UEmoji.ARROW_LEFT, self.on_arrow_left)
		self.add_button(UEmoji.ARROW_RIGHT, self.on_arrow_right)

	async def send_initial_message(self) -> discord.Message:
		return await self.ctx.send(embed=self.embeds[self._start_page])

	async def update(self):
		await self.message.edit(embed=self.embeds[self.current_page])

	async def on_arrow_left(self):
		self.current_page = max(0, self.current_page - 1)

	async def on_arrow_right(self):
		self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
