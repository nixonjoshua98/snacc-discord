import discord

from discord.ext import menus

from src.common.emoji import Emoji


class DisplayPages(menus.Menu):
	def __init__(self, pages, timeout: int = 180):
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

	async def on_reaction_extra(self, payload, index_change):
		self.current = max(0, min(len(self.pages) - 1, self.current + index_change))

	async def on_reaction(self, payload, index_change):
		await self.on_reaction_extra(payload, index_change)

		current = self.pages[self.current]

		if self.message.guild is not None and self.bot.has_permissions(self.message.channel, manage_messages=True):
			await self.message.remove_reaction(payload.emoji, payload.member)

		if isinstance(current, discord.Embed):
			return await self.message.edit(content=None, embed=current)

		await self.message.edit(content=current, embed=None)

	@menus.button(Emoji.REWIND)
	async def go_first(self, payload):
		await self.on_reaction(payload, -self.current)

	@menus.button(Emoji.ARROW_LEFT)
	async def go_prev(self, payload):
		await self.on_reaction(payload, -1)

	@menus.button(Emoji.ARROW_RIGHT)
	async def go_next(self, payload):
		await self.on_reaction(payload, 1)

	@menus.button(Emoji.FAST_FORWARD)
	async def go_last(self, payload):
		await self.on_reaction(payload, len(self.pages) - self.current - 1)

	async def send(self, ctx, *, send_dm: bool = False, wait: bool = False):
		if len(self.pages) == 1:
			return await self.send_initial_message(ctx, ctx.channel)

		chnl = ctx.channel if not send_dm else await ctx.author.create_dm()

		await self.start(ctx, channel=chnl, wait=wait)
