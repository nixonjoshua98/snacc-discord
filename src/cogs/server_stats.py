from discord.ext import commands

from src.common import checks


class ServerStats(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_any_bot_channel(ctx) and commands.guild_only()

	@commands.command(name="size", description="Server size")
	async def size(self, ctx):
		await ctx.send(f"This server has ``{ctx.guild.member_count}`` members")
