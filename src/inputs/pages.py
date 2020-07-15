import discord

from src.common.emoji import Emoji

from .reactionmenubase import ReactionMenuBase, button


class Pages(ReactionMenuBase):
	def __init__(self, bot, author, pages):
		super().__init__(bot, author)

		self.pages = pages

		self.current_page = 0

	def get_next_message(self):
		page = self.pages[self.current_page]

		embed = page if isinstance(page, discord.Embed) else None
		content = page if isinstance(page, str) else None

		return embed, content

	async def add_reactions(self):
		if len(self.pages) > 1:
			await super().add_reactions()

	async def send_initial_message(self, destination) -> discord.Message:
		embed, content = self.get_next_message()

		return await destination.send(embed=embed, content=content)

	async def on_update(self):
		embed, content = self.get_next_message()

		await self.edit_message(embed=embed, content=content)

	@button(Emoji.REWIND, index=0)
	async def first_page(self):
		self.current_page = 0

	@button(Emoji.ARROW_RIGHT, index=2)
	async def prev_page(self):
		self.current_page = min(len(self.pages) - 1, self.current_page + 1)

	@button(Emoji.ARROW_LEFT, index=1)
	async def next_page(self):
		self.current_page = max(0, self.current_page - 1)

	@button(Emoji.FAST_FORWARD, index=3)
	async def last_page(self):
		self.current_page = len(self.pages) - 1



