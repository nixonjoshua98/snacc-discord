import discord

from datetime import datetime

from discord.ext import commands

from src.menus.menubase import MenuBase

from src.common.emoji import Emoji


class YesNoMenu(MenuBase):
	def __init__(self, bot: commands.Bot, question):
		super().__init__(bot, delete_after=True, timeout=60.0)

		self.question = question

		self.answer = None

		self.add_buttons()

	def get(self):
		return self.answer

	def add_buttons(self):
		self.add_button(Emoji.TICK, self.on_yes)
		self.add_button(Emoji.CROSS, self.on_no)

	async def send_initial_message(self, destination: discord.abc.Messageable) -> discord.Message:
		today = datetime.utcnow().strftime('%d/%m/%Y %X')

		embed = discord.Embed(title="Yes or No?", colour=discord.Color.orange(), description=self.question)

		embed.set_footer(text=f"{self._bot.user.name} | {today}", icon_url=self._bot.user.avatar_url)

		return await destination.send(embed=embed)

	async def update_message(self) -> bool:
		embed: discord.Embed = self._message.embeds[0]

		txt = "Yes" if self.answer else "Timed out" if self.answer is None else "No"

		embed.insert_field_at(0, name="Author Response", value=f"{txt}")

		await self._message.edit(embed=embed)

		return True

	async def on_yes(self):
		self.answer = True

	async def on_no(self):
		self.answer = False
