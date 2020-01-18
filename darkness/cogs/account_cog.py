from discord.ext import commands


class Account(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="join")
	async def joined(self, ctx):
		# Sends a message of when the user joined the server

		date = ctx.author.joined_at.strftime("%B %d, %Y")

		msg = f"``{ctx.author.display_name}`` joined the server on {date}"

		await ctx.send(msg)

	@commands.command(name="created")
	async def created(self, ctx):
		# Sends a message which contains the date which the account was created

		date = ctx.author.created_at.strftime("%B %d, %Y")

		msg = f"The ``{ctx.author.display_name}`` account was created on {date}"

		await ctx.send(msg)
