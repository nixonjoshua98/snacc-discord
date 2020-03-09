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
			description=f"{pet_stats['name']} | Lvl: {self.level_from_xp(pet_stats['xp'])}",
			color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		stats_text = (
			f":heart: {pet_stats['health']:,}\n"
			f":crossed_swords: {pet_stats['attack']:,}\n"
			f":shield: {pet_stats['defence']:,}"
		)

		embed.add_field(name="Stats", value=stats_text)

		await ctx.send(embed=embed)

	@commands.command(name="setname", help="Set name of pet")
	async def set_name(self, ctx: commands.Context, pet_name: str):
		"""
		Set name of the authors pet

		:param ctx: Discord context
		:param pet_name: New pet name
		:return:
		"""
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

			pet_stats["name"] = pet_name

			file.set(str(ctx.author.id), pet_stats)

		await ctx.send(f"**{ctx.author.display_name}** has renamed their pet to **{pet_name}**")

	@commands.command(name="fight", aliases=["battle", "attack"], help="Attack another pet")
	async def fight(self, ctx: commands.Context, target: discord.Member):
		if target.id == ctx.author.id:
			return await ctx.send(f"**{ctx.author.display_name}** you cannot fight yourself")

		with FileReader("pet_stats.json") as file:
			author_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)
			target_stats = file.get(str(target.id), self.DEFAULT_STATS)

		# Create embed
		embed = discord.Embed(
			title="Pet Battle",
			description=f"{author_stats['name']} vs {target_stats['name']}",
			color=0xff8000)

		embed.add_field(name="How to Play", value="Choose a reaction")

		# Send initial message
		message = await ctx.send(embed=embed)

		# Spade, Heart, Club, Diamond
		reactions = ["\U00002660", "\U00002665", "\U00002663", "\U00002666"]

		# Reactions
		for emoji in reactions:
			await message.add_reaction(emoji)

		# Wait for reaction from user
		await self.bot.wait_for(
			"reaction_add",
			timeout=60,
			check=lambda react, user: user.id == ctx.author.id and react.emoji in reactions
		)

		await ctx.send(f"{ctx.author.display_name} has lost 10,000 coins for losing")


	@commands.command(name="petlb", aliases=["plb"], help="Show the  pet leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		"""
		Shows the pet leaderboard

		:param ctx: The message context
		:return:
		"""
		leaderboard_string = await leaderboard.create_leaderboard(ctx.author, leaderboard.Type.PET)

		await ctx.send(leaderboard_string)









