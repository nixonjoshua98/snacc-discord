import discord

from discord.ext import menus

from src.common.emoji import Emoji


class DisplayPages(menus.Menu):
	def __init__(self, pages, timeout: int = 180.0):
		super().__init__(timeout=timeout, clear_reactions_after=True)

		self.current = 0

		self.pages = pages

	async def send_initial_message(self, _, destination):
		current = self.pages[self.current]

		if isinstance(current, discord.Embed):
			return await destination.send(embed=current)

		return await destination.send(current)

	def reaction_check(self, payload):
		if self.message.guild is not None and payload.event_type == "REACTION_REMOVE":
			return False

		return super(DisplayPages, self).reaction_check(payload)

	async def on_reaction(self, payload):
		current = self.pages[self.current]

		if self.message.guild is not None and self.bot.has_permissions(self.message.channel, manage_messages=True):
			await self.message.remove_reaction(payload.emoji, self.ctx.author)

		if isinstance(current, discord.Embed):
			return await self.message.edit(content=None, embed=current)

		return await self.message.edit(content=current, embed=None)

	@menus.button(Emoji.REWIND)
	async def go_first(self, payload):
		self.current = 0

		await self.on_reaction(payload)

	@menus.button(Emoji.ARROW_LEFT)
	async def go_prev(self, payload):
		self.current = max(0, self.current - 1)

		await self.on_reaction(payload)

	@menus.button(Emoji.ARROW_RIGHT)
	async def go_next(self, payload):
		self.current = min(len(self.pages) - 1, self.current + 1)

		await self.on_reaction(payload)

	@menus.button(Emoji.FAST_FORWARD)
	async def go_last(self, payload):
		self.current = len(self.pages) - 1

		await self.on_reaction(payload)

	async def send(self, ctx, *, send_dm: bool = False, wait: bool = False):
		if len(self.pages) == 1:
			return await self.send_initial_message(ctx, ctx.channel)

		if send_dm:
			await self.start(ctx, channel=await ctx.author.create_dm(), wait=wait)

		else:
			await self.start(ctx, channel=ctx.channel, wait=wait)
