from discord.ext import commands

from darkness.common import data_reader


class Server(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._server_config = data_reader.read_json("server_config.json")

	@commands.command(name="size", description="Server member count")
	async def size(self, ctx):
		# Returns the server size
		await ctx.send(f"This server has ``{ctx.guild.member_count}`` members")

	@commands.command(name="invite", description="Server invite link")
	async def invite(self, ctx):
		# Returns the invite link for the server
		await ctx.send(self._server_config["invite_link"])