import discord

from discord.ext import commands

from src.common import checks
from src.common import myjson
from src.common import FileReader


class Pet(commands.Cog, name="pet"):
	DEFAULT_STATS = {
		"name": "Pet",
		"level": 1,
		"health": 100,
		"attack": 10,
		"defence": 10,
		"wins": 0,
		"loses": 0
	}

	def __init__(self, bot):
		self.bot = bot

		myjson.download_file("pet_stats.json")

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx)

	@commands.command(name="pet", aliases=["p"], help="Display your pet stats")
	async def pet(self, ctx: commands.Context):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

		embed = discord.Embed(
			title=ctx.author.display_name,
			description=f"{pet_stats['name']} | Level: {pet_stats['level']}",
			color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		for k, v in self.DEFAULT_STATS.items():
			if k in {"name", "level"}:
				continue

			embed.add_field(name=k.title(), value=v, inline=True)

		await ctx.send(embed=embed)

	@commands.command(name="setname", help="Set name of pet")
	async def set_name(self, ctx: commands.Context, pet_name: str):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

			pet_stats["name"] = pet_name

			file.set(str(ctx.author.id), pet_stats)

		await ctx.send(f"**{ctx.author.display_name}**s pet has been renamed to **{pet_name}**")
