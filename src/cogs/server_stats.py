from discord.ext import commands

from src.common import checks


class ServerStats(commands.Cog, name="server"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_any_bot_channel(ctx)

	@commands.command(name="size", help="Member count")
	async def size(self, ctx):
		await ctx.send(f"This server has ``{ctx.guild.member_count}`` members")
