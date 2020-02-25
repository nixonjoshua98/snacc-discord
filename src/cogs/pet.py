import asyncio

from discord.ext import commands

from src.common import checks


class Pet(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx) and commands.guild_only()

	@commands.command(name="pet", aliases=["p"], help="Display your pet stats")
	async def pet(self, ctx):
		message = await ctx.send(f"**{ctx.author.display_name}** will be banned in 3")

		await asyncio.sleep(1.0)

		for i in range(2):
			await message.edit(content=f"**{ctx.author.display_name}** will be banned in {2-i}")

			await asyncio.sleep(1.0)

		await message.edit(content=f"**{ctx.author.display_name}** has been banned :slight_smile:")
