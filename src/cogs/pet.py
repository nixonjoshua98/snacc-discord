import discord

from discord.ext import commands

from src.common import checks
from src.common import myjson
from src.common import FileReader
from src.common import leaderboard

class Pet(commands.Cog, name="pet"):
	DEFAULT_STATS = {
		"name": "Pet",
		"xp": 0,
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

	@staticmethod
	def level_from_xp(xp: int) -> int:
		return 0

	@commands.command(name="pet", aliases=["p"], help="Display your pet stats")
	async def pet(self, ctx: commands.Context):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

		embed = discord.Embed(
			title=ctx.author.display_name,
			description=f"{pet_stats['name']} | XP: {pet_stats['xp']}",
			color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		embed.add_field(name="Health", 	value=pet_stats["health"], 								inline=True)
		embed.add_field(name="Atk/Def",	value=f'{pet_stats["attack"]}/{pet_stats["defence"]}', 	inline=True)
		embed.add_field(name="W/L",		value=f'{pet_stats["wins"]}/{pet_stats["loses"]}', 		inline=True)

		await ctx.send(embed=embed)

	@commands.command(name="setname", help="Set name of pet")
	async def set_name(self, ctx: commands.Context, pet_name: str):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

			pet_stats["name"] = pet_name

			file.set(str(ctx.author.id), pet_stats)

		await ctx.send(f"**{ctx.author.display_name}** has renamed their pet to **{pet_name}**")

	@commands.command(name="fight", aliases=["battle", "attack"], help="Attack another pet")
	async def fight(self, ctx: commands.Context, target: discord.Member):
		pass

	@commands.command(name="petlb", aliases=["plb"], help="Show the  pet leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		"""
		Shows the pet leaderboard

		:param ctx: The message context
		:return:
		"""
		leaderboard_string = await leaderboard.create_leaderboard(ctx.author, leaderboard.Type.PET)

		await ctx.send(leaderboard_string)