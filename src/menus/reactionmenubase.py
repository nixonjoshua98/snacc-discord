import discord
import asyncio

from discord.ext import commands

from src.menus.menubase import MenuBase


class ReactionMenuBase(MenuBase):
	def __init__(self, bot: commands.Bot, **options):
		super().__init__(bot, **options)

		self._message = None
		self._buttons = dict()

		self._delete_after = options.get("delete_after", False)

	async def on_reaction_add(self, react: discord.Reaction) -> bool:
		callback = self._buttons.get(str(react.emoji))

		if callback is not None:
			await callback()

		return callback is not None

	async def send_initial_message(self, destination: commands.Context) -> discord.Message: ...

	async def update_message(self) -> bool:
		return False

	async def send(self, destination: commands.Context):
		self._message = await self.send_initial_message(destination)

		await self._add_reactions()

		self._destination = destination

		def wait_for(react_, user_):
			return self._destination.author.id == user_.id and react_.message.id == self._message.id

		while True:
			try:
				react, user = await self._bot.wait_for("reaction_add", timeout=self._timeout, check=wait_for)

			except asyncio.TimeoutError:
				return await self.after_menu_expire()

			else:
				react_has_callback = await self.on_reaction_add(react)

				await self._remove_react(react, user)

				if react_has_callback and await self.update_message():
					return await self.after_menu_expire()

	async def after_menu_expire(self):
		try:
			if self._delete_after:
				await self._message.delete()

			else:
				await self._message.clear_reactions()

		except (discord.HTTPException, discord.Forbidden):
			pass

	def add_button(self, emoji, callback):
		self._buttons[emoji] = callback

	async def _add_reactions(self):
		for emoji in self._buttons:
			await self._message.add_reaction(emoji)

	async def _clear_reactions(self):
		await self._message.clear_reactions()
