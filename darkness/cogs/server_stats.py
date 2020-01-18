from discord.ext import commands

from darkness.common import data_reader


class ServerStats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._config = data_reader.read_json("server_config.json")

	@commands.command(name="size")
	async def size(self, ctx):
		await ctx.send(f"This server has ``{ctx.guild.member_count}`` members")

	@commands.command(name="joined")
	async def joined(self, ctx):
		date = ctx.author.joined_at.strftime("%B %d, %Y")

		msg = f"``{ctx.author.display_name}`` joined the server on {date}"

		await ctx.send(msg)

	@commands.command(name="created")
	async def created(self, ctx):
		date = ctx.author.created_at.strftime("%B %d, %Y")

		msg = f"The ``{ctx.author.display_name}`` account was created on {date}"

		await ctx.send(msg)