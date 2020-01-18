from discord.ext import commands

from darkness.common import data_reader


class ServerStats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._server_config = data_reader.read_json("server_config.json")

	@commands.command(name="size")
	async def size(self, ctx):
		"""
		Sends a message containing the member count of the server

		:param ctx: The message send in the server
		:return:
		"""

		await ctx.send(f"This server has ``{ctx.guild.member_count}`` members")

	@commands.command(name="invite")
	async def invite(self, ctx):
		await ctx.send(self._server_config["invite_link"])