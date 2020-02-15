import discord


class TestGuildMember:
	def __init__(self, _id: int, server: discord.Guild):
		self._id = _id
		self._server = server
