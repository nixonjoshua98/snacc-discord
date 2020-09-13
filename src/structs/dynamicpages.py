import discord

from discord.ext import menus

from src.common.emoji import Emoji


class DynamicPages(menus.Menu):
	def __init__(self, pages, func, timeout: int = 180):
		super().__init__(timeout=timeout, clear_reactions_after=True)

		self.current = 0

		self.dynamic_func = func

		self.pages = pages

	async def send_initial_message(self, _, destination):
		current = self.pages[self.current]

		if isinstance(current, discord.Embed):
			return await destination.send(embed=current)

		return await destination.send(current)

	def reaction_check(self, payload):
		if self.message.guild is not None and payload.event_type == "REACTION_REMOVE":
			return False

		return super(DynamicPages, self).reaction_check(payload)

	async def on_reaction(self, payload, index_change):
		self.current = await self.dynamic_func(self.current, index_change, self.pages)

		current = self.pages[self.current]

		if self.message.guild is not None and self.bot.has_permissions(self.message.channel, manage_messages=True):
			await self.message.remove_reaction(payload.emoji, self.ctx.author)

		if isinstance(current, discord.Embed):
			return await self.message.edit(content=None, embed=current)

		return await self.message.edit(content=current, embed=None)

	@menus.button(Emoji.ARROW_LEFT)
	async def go_prev(self, payload):
		await self.on_reaction(payload, -1)

	@menus.button(Emoji.ARROW_RIGHT)
	async def go_next(self, payload):
		await self.on_reaction(payload, 1)

	async def send(self, ctx, *, send_dm: bool = False, wait: bool = False):
		chnl = ctx.channel if not send_dm else await ctx.author.create_dm()

		await self.start(ctx, channel=chnl, wait=wait)
