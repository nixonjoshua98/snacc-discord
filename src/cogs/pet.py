import discord
import random
import asyncio

from discord.ext import commands

from src.common import checks
from src.common import functions
from src.common import converters
from src.common import FileReader

from src.structures import Leaderboard


class Pet(commands.Cog, name="pet"):
	ATTACK_REACTIONS = ["\U00002660", "\U00002665", "\U00002663", "\U00002666"]
	DEFAULT_STATS = {"name": "Pet", "xp": 0, "health": 100}

	def __init__(self, bot):
		self.bot = bot

		self._leaderboard = Leaderboard(
			title="Global Pet Leaderboard",
			file="pet_stats.json",
			columns=["name", "xp"],
			sort_func=lambda kv: kv[1]["xp"]
		)

		self._leaderboard.update_column("xp", "level", lambda data: Pet.get_pet_level(data))

	async def cog_check(self, ctx):
		return await checks.requires_channel_tag("game")(ctx)

	@staticmethod
	def get_pet_level(data: dict) -> int:
		return data.get("xp", 0) // 50

	@staticmethod
	def get_pet_attack(data: dict) -> int:
		return 10 + (Pet.get_pet_level(data) * 5)

	@staticmethod
	def get_pet_defence(data: dict) -> int:
		return 10 + (Pet.get_pet_level(data) * 5)

	@commands.command(name="pet", aliases=["p"], help="Display your pet stats")
	async def pet(self, ctx: commands.Context):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

		stats_text = (
			f":heart: {pet_stats.get('health', 100):,}\n"
			f":crossed_swords: {Pet.get_pet_attack(pet_stats):,}\n"
			f":shield: {Pet.get_pet_defence(pet_stats):,}"
		)

		desc = f"{pet_stats['name']} | Lvl: {Pet.get_pet_level(pet_stats)}"
		embed = functions.create_embed(ctx.author.display_name, desc, ctx.author.avatar_url)
		embed.add_field(name="Stats", value=stats_text)

		await ctx.send(embed=embed)

	@commands.command(name="setname", help="Set name of pet")
	async def set_name(self, ctx: commands.Context, new_pet_name: str):
		with FileReader("pet_stats.json") as pet_stats:
			pet_stats.set_inner_key(str(ctx.author.id), "name", new_pet_name)

		await ctx.send(f"**{ctx.author.display_name}** has renamed their pet to **{new_pet_name}**")

	@commands.cooldown(1, 60 * 3, commands.BucketType.user)
	@commands.command(name="fight", help="Attack! [60s]")
	async def fight(self, ctx: commands.Context, defender: converters.ValidUser()):
		def wait_for_react(react, user_):
			return user_.id == ctx.author.id and react.emoji in self.ATTACK_REACTIONS and react.message.id == message.id

		# - - - LOAD DATA - - -
		with FileReader("pet_stats.json") as file:
			author_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)
			target_stats = file.get(str(defender.id), self.DEFAULT_STATS)
		# - - - - - - - - - - -

		# - - - SEND MESSAGE - - -
		message = await self.create_pet_attack_menu(ctx, author_stats, target_stats)

		embed = message.embeds[0]
		# - - - - - - - - - - - -

		# - - - WAIT FOR USER INPUT - - -
		try:
			await self.bot.wait_for("reaction_add", timeout=60, check=wait_for_react)
		except asyncio.TimeoutError:
			embed.set_field_at(0, name="Battle Report", value="Timed out")

			return await message.edit(embed=embed)

		message = discord.utils.get(self.bot.cached_messages, id=message.id)
		# - - - - - - - - - - - - - - - -

		# - - - PERFORM ATTACK - - -
		attack_index = await functions.get_reaction_index(ctx.author, message)

		rewards = self.perform_pet_attack(attack_index, ctx.author, defender)
		# - - - - - - - - - - - - -

		if rewards.get("error", None) is not None:
			embed.set_field_at(0, name="Report", value=rewards["error"], inline=False)

		else:
			battle_report = f":moneybag: {rewards['coins']} :star: {rewards['xp']}"

			embed.set_field_at(0, name="Battle Report", value=battle_report, inline=False)

			if rewards.get("log", []):
				embed.add_field(name="Battle Log", value="\n".join(rewards["log"]), inline=False)

		await message.edit(embed=embed)

	async def create_pet_attack_menu(self, ctx: commands.Context, attacker: dict, defender: dict) -> discord.Message:
		desc = f"**'{attacker['name']}'** vs **'{defender['name']}'**"

		# - - - Create Embed - - -
		embed = functions.create_embed("Pet battle", desc, ctx.author.avatar_url)
		embed.add_field(name="How to Play", value="Select a reaction")
		# - - -

		msg = await ctx.send(embed=embed)

		for emoji in self.ATTACK_REACTIONS:
			await msg.add_reaction(emoji)

		return msg

	def perform_pet_attack(self, _: int, attacker: discord.Member, defender: discord.Member):
		log = []

		with FileReader("pet_stats.json") as pet_file, FileReader("coins.json") as coins_file:
			# - - - READ DATA - - -
			attacker_pet = pet_file.get(str(attacker.id), self.DEFAULT_STATS)
			defender_pet = pet_file.get(str(defender.id), self.DEFAULT_STATS)

			attacker_coins = coins_file.get_inner_key(str(attacker.id), "coins", 0)
			# - - - - - - - - - - -

			# - - - CALCULATE STATS - - -
			atk_atk, atk_def = Pet.get_pet_attack(attacker_pet), Pet.get_pet_defence(attacker_pet)
			def_atk, def_def = Pet.get_pet_attack(defender_pet), Pet.get_pet_defence(defender_pet)

			initial_pet_level = Pet.get_pet_level(attacker_pet)
			# - - - - - - - - - - - - - -

			# - - - CALCULATE REWARDS - - -
			health_lost = min(15, max(1, def_def - atk_atk))

			coins_gained = random.randint(10, 25) + max(1, def_def - atk_atk) * random.randint(5, 8)
			xp_gained = random.randint(10, 25)
			# - - - - - - - - - - - - - - -

			# - - - CHECK ATTACKER FAINT - - -
			if health_lost > attacker_pet.get("health", 100):
				return {"error": f"{attacker_pet['name']} fainted during battle**"}
			# - - - - - - - - - - - - - - - - -

			# - - - UPDATE LOCAL STATS - - -
			attacker_pet["health"] -= health_lost
			attacker_coins += coins_gained
			attacker_pet["xp"] += xp_gained
			# - - - - - - - - - - - - - - -

			# - - - LEVEL UP - -
			new_pet_level = Pet.get_pet_level(attacker_pet)
			if new_pet_level > initial_pet_level:
				log.append(f"{attacker_pet['name']} is now level {new_pet_level}!")
			# - - - - - - - - -

			# - - - SET DATA - - -
			pet_file.set(str(attacker.id), attacker_pet)
			coins_file.set_inner_key(str(attacker.id), "coins", attacker_coins)
			# - - - - - - - - - - -

		return {"log": log, "coins": coins_gained, "xp": xp_gained}

	@commands.command(name="petlb", aliases=["plb"], help="Show the pet leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		leaderboard_string = await self._leaderboard.create(ctx.author)

		await ctx.send(leaderboard_string)









