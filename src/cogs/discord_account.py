from discord.ext import commands

from src.common import checks


class DiscordAccount(commands.Cog, name="Account"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_any_bot_channel(ctx)

	@commands.command(name="join", description="Date user joined the server")
	async def joined(self, ctx):
		date = ctx.author.joined_at.strftime("%B %d, %Y")

		msg = f"``{ctx.author.display_name}`` joined the server on {date}"

		await ctx.send(msg)

	@commands.command(name="created", description="Account creation date")
	async def created(self, ctx):
		date = ctx.author.created_at.strftime("%B %d, %Y")

		msg = f"The ``{ctx.author.display_name}`` account was created on {date}"

		await ctx.send(msg)
