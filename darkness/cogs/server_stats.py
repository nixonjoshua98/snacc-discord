from discord.ext import commands

from darkness.common import data_reader


class ServerStats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._config = data_reader.read_json("server_config.json")

	@commands.command(name="size")
	async def size(self, ctx):
		await ctx.send(f"The darkness has taken over ``{ctx.guild.member_count}`` accounts!")