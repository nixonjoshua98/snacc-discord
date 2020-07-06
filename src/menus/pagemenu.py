import discord

from discord.ext import commands

from src.menus.menubase import MenuBase

from src.common.emoji import Emoji


class PageMenu(MenuBase):
	def __init__(self, bot: commands.Bot, pages, **options):
		super().__init__(bot, **options)

		self._page = 0
		self._pages = pages

		self.add_buttons()

	def add_buttons(self):
		if len(self._pages) > 1:
			self.add_button(Emoji.REWIND, self.on_rewind)
			self.add_button(Emoji.ARROW_LEFT, self.on_arrow_left)
			self.add_button(Emoji.ARROW_RIGHT, self.on_arrow_right)
			self.add_button(Emoji.FAST_FORWARD, self.on_fast_forward)

	async def send_initial_message(self, destination: discord.abc.Messageable) -> discord.Message:
		content, embed = self.get_next_message()

		return await destination.send(content=content, embed=embed)

	async def update_message(self):
		content, embed = self.get_next_message()

		await self._message.edit(content=content, embed=embed)

	def get_next_message(self):
		page = self._pages[self._page]

		content = page if isinstance(page, str) else None
		embed = page if isinstance(page, discord.Embed) else None

		return content, embed

	async def on_rewind(self):
		self._page = 0

	async def on_arrow_left(self):
		self._page = max(0, self._page - 1)

	async def on_arrow_right(self):
		self._page = min(len(self._pages) - 1, self._page + 1)

	async def on_fast_forward(self):
		self._page = len(self._pages) - 1
