import discord

from src.common.emoji import Emoji

from .reactionmenubase import ReactionMenuBase, button


class Confirmation(ReactionMenuBase):
	def __init__(self, bot, author, question):
		super().__init__(bot, author, timeout=15.0)

		self.question = question

		self.answer = None

	def get(self):
		return self.answer

	async def send_initial_message(self, destination: discord.abc.Messageable) -> discord.Message:
		embed = discord.Embed(title=self.question, colour=discord.Color.orange())

		return await destination.send(embed=embed)

	async def on_update(self) -> bool:
		await super().on_update()
		await self.delete_message()

		self.is_ended = True

	async def on_timeout(self):
		await super().on_timeout()
		await self.delete_message()

	@button(Emoji.TICK, index=0)
	async def confirm(self):
		self.answer = True

	@button(Emoji.CROSS, index=1)
	async def cancel(self):
		self.answer = False
