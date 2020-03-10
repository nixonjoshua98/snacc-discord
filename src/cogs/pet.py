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
		return await checks.in_game_channel(ctx)

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

	@commands.cooldown(1, 60, commands.BucketType.user)
	@commands.command(name="fight", aliases=["battle", "attack"], help="Attack! [5m Cooldown]")
	async def fight(self, ctx: commands.Context, target: discord.Member):
		if target.id == ctx.author.id or target.bot:
			return await ctx.send(f"**{ctx.author.display_name}** :face_with_raised_eyebrow:")

		with FileReader("pet_stats.json") as file:
			author_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)
			target_stats = file.get(str(target.id), self.DEFAULT_STATS)

		# Create embed
		embed = discord.Embed(
			title="Pet Battle",
			description=f"**'{author_stats['name']}'** vs **'{target_stats['name']}'**",
			color=0xff8000)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		# Set fields
		embed.add_field(name="How to Play", value="Select a reaction")

		# Send initial message
		message = await ctx.send(embed=embed)

		# Spade, Heart, Club, Diamond
		reactions = ["\U00002660", "\U00002665", "\U00002663", "\U00002666"]

		# Add reactions
		for emoji in reactions:
			await message.add_reaction(emoji)

		# Wait for reaction from user
		await self.bot.wait_for("reaction_add", timeout=60,
			check=lambda react, user: user.id == ctx.author.id and react.emoji in reactions and message.id == react.message.id
		)

		reaction_index = None

		# Refresh the message
		message = discord.utils.get(self.bot.cached_messages, id=message.id)

		# Find which reaction the user chose
		for i, reaction in enumerate(message.reactions):
			if reaction_index is not None:
				break

			for user in await reaction.users().flatten():
				if user.id == ctx.author.id:
					reaction_index = i
					break

		if reaction_index is None:
			return await ctx.send(f"**{ctx.author.display_name}**, your pet battle caused an error")

		# Pet Battle

		# Reward text
		battle_report = (
			f":heart: 0\n"
			f":moneybag: 0\n"
			f":star: 0"
		)

		embed.remove_field(0)

		embed.add_field(name="Battle Report", value=battle_report)

		await message.edit(embed=embed)

	@commands.command(name="petlb", aliases=["plb"], help="Show the  pet leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		"""
		Shows the pet leaderboard

		:param ctx: The message context
		:return:
		"""
		leaderboard_string = await leaderboard.create_leaderboard(ctx.author, leaderboard.Type.PET)

		await ctx.send(leaderboard_string)









