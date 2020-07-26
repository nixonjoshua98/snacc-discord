import discord


class InputBase:
	def __init__(self, bot, author, **options):
		self.bot = bot
		self.author = author

		self.is_ended = False

		self.timeout = options.get("timeout", 180.0)

		self.message = None
		self.destination = None

	async def send(self, destination):
		self.destination = destination

		self.message = await self.send_initial_message(destination)

	@staticmethod
	async def remove_reaction(react, user):
		try:
			await react.remove(user)

		except (discord.Forbidden, discord.HTTPException):
			""" Failed. """

	async def clear_reactions(self):
		try:
			if self.message.guild is not None:
				await self.message.clear_reactions()

			else:
				self.message = await self.message.channel.fetch_message(self.message.id)

				for react in self.message.reactions:
					await self.remove_reaction(react, self.message.author)

		except (discord.Forbidden, discord.HTTPException):
			""" Failed. """

	async def edit_message(self, content=None, embed=None):
		try:
			await self.message.edit(content=content, embed=embed)

		except (discord.Forbidden, discord.HTTPException):
			""" Failed. """

	async def delete_message(self):
		try:
			await self.message.delete()

		except (discord.Forbidden, discord.HTTPException):
			""" Failed. """

	async def send_initial_message(self, destination) -> discord.Message: ...

	def wait_for(self, *args, **kwargs): ...
