from discord.ext import menus


class Confirm(menus.Menu):
	def __init__(self, msg, timeout: int = 30.0):
		super().__init__(timeout=timeout, delete_message_after=True)

		self.msg = msg

		self.result = None

	async def send_initial_message(self, ctx, channel):
		return await channel.send(self.msg)

	@menus.button('\N{WHITE HEAVY CHECK MARK}')
	async def do_confirm(self, _):
		self.result = True

		self.stop()

	@menus.button('\N{CROSS MARK}')
	async def do_deny(self, _):
		self.result = False

		self.stop()

	async def prompt(self, ctx):
		await self.start(ctx, wait=True)

		return self.result
