
from src.structs.displaypages import DisplayPages


class DynamicPages(DisplayPages):
	def __init__(self, pages, func, timeout: int = 180):
		super().__init__(pages, timeout)

		self.current = 0

		self.dynamic_func = func

		self.pages = pages

	async def on_reaction_extra(self, payload, index_change):
		self.current = await self.dynamic_func(self.current, index_change, self.pages)

	async def send(self, ctx, *, send_dm: bool = False, wait: bool = False):
		chnl = ctx.channel if not send_dm else await ctx.author.create_dm()

		await self.start(ctx, channel=chnl, wait=wait)
