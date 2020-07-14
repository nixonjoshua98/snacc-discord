import string
import discord

import functools as ft

from src.common.emoji import Emoji

from .reactionmenubase import ReactionMenuBase


class OptionMenu(ReactionMenuBase):
	def __init__(self, bot, author, title, options):
		super().__init__(bot, author)

		self.title = title
		self.options = options

		self.response = None

		self.add_options()

	def add_options(self):
		for i, opt in enumerate(self.options):
			self.add_button(Emoji.LETTERS[i], ft.partial(self.on_react_event, i), i)

	async def send_initial_message(self, destination) -> discord.Message:
		embed = discord.Embed(title=self.title, colour=discord.Color.orange())

		s = []

		for i, opt in enumerate(self.options):
			s.append(f":regional_indicator_{string.ascii_lowercase[i]}: {opt}")

		embed.description = "\n".join(s)

		return await destination.send(embed=embed)

	def get(self):
		return self.response

	async def on_react_event(self, index):
		embed = self.message.embeds[0]

		embed.description = f":regional_indicator_{string.ascii_lowercase[index]}: {self.options[index]}"

		await self.edit_message(embed=embed)

		self.response = self.options[index]

		self.is_ended = True
