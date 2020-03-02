import discord

from discord.ext import commands

from src.common import checks
from src.common import FileReader


class Pet(commands.Cog, name="pet"):
	DEFAULT_STATS = {
		"level": 1,
		"attack": 10,
		"defence": 10,
		"health": 100,
		"wins": 0,
		"loses": 0
	}

	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx)

	@commands.command(name="pet", aliases=["p"], help="Display your pet stats")
	async def pet(self, ctx):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

		embed = discord.Embed(title=ctx.author.display_name, description=f"Pet Stats", color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		for k, v in pet_stats.items():
			embed.add_field(name=k.title(), value=v, inline=True)

		await ctx.send(embed=embed)
