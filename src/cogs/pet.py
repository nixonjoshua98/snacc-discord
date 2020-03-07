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
		with FileReader("pet_stats.json") as file:
			user_pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

			target_pet_stats = file.get(str(target.id), self.DEFAULT_STATS)

	@commands.command(name="petlb", aliases=["plb"], help="Show the  pet leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		def get_user_rank(val) -> int:
			try:
				return data.index(val) + 1
			except ValueError:
				return len(data)
		"""
		Shows the pet leaderboard

		:param ctx: The message context
		:return:
		"""
		with FileReader("pet_stats.json") as file:
			data = sorted(file.data().items(), key=lambda k: k[1]["level"], reverse=True)

			user_data = (str(ctx.author.id), file.get(str(ctx.author.id), default_val=self.DEFAULT_STATS))

		# Only show top 10 members
		leaderboard_size = 10
		top_players = data[0: leaderboard_size]

		# Max username length
		max_username_length = 25
		user_rank = get_user_rank(user_data)

		# used for '---'
		row_length = 1

		msg = f"```c++\nPet Leaderboard\n\n    Username{' ' * (max_username_length - 7)}Level"

		for rank, (user_id, pet_stats) in enumerate(top_players, start=1):
			user = ctx.guild.get_member(int(user_id))

			username = user.display_name + f" ({pet_stats['name']})"
			username = username[0:max_username_length] if user else "> User Left <"

			row = f"\n#{rank:02d} {username}{' ' * (max_username_length - len(username)) + ' '}{pet_stats['level']:02d}"

			msg += row
			row_length = max(row_length, len(row))
			rank += 1

		username = ctx.author.display_name[0:max_username_length] + f" ({user_data[1]['name']})"
		row = f"\n#{user_rank:02d} {username}{' ' * (max_username_length - len(username)) + ' '}{user_data[1]['level']:02d}"
		msg += "\n" + "-" * row_length + "\n" + row

		msg += "```"

		await ctx.send(msg)