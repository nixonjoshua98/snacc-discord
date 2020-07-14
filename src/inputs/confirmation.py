import discord

from src.common.emoji import Emoji

from .reactionmenubase import ReactionMenuBase, button


class Confirmation(ReactionMenuBase):
	def __init__(self, bot, author, question):
		super().__init__(bot, author)

		self.question = question

		self.answer = None

	def get(self):
		return self.answer

	async def send_initial_message(self, destination: discord.abc.Messageable) -> discord.Message:
		embed = discord.Embed(title=self.question, colour=discord.Color.orange())

		return await destination.send(embed=embed)

	async def on_update(self) -> bool:
		embed: discord.Embed = self.message.embeds[0]

		txt = "Yes" if self.answer else "Timed out" if self.answer is None else "No"

		embed.description = txt

		await self.message.edit(embed=embed)

		self.is_ended = True

	@button(Emoji.TICK, index=0)
	async def confirm(self):
		self.answer = True

	@button(Emoji.CROSS, index=1)
	async def cancel(self):
		self.answer = False
