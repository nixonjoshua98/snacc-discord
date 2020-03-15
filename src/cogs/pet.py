import discord
import asyncio

from discord.ext import commands

from src.common import checks
from src.common import functions
from src.common import converters
from src.common import FileReader

from src.structures import Leaderboard


class Pet(commands.Cog, name="pet"):
	ATTACK_REACTIONS = ["\U00002660", "\U00002665", "\U00002663", "\U00002666"]
	DEFAULT_STATS = {"name": "Pet", "xp": 0, "health": 100, "attack": 10, "defence": 10, "wins": 0, "loses": 0}

	def __init__(self, bot):
		self.bot = bot

		self._leaderboard = Leaderboard(
			title="Global Pet Leaderboard",
			file="pet_stats.json",
			columns=["name", "xp"],
			sort_func=lambda kv: kv[1]["xp"]
		)

		self._leaderboard.update_column("xp", "level", lambda data: functions.pet_level_from_xp(data))

	async def cog_check(self, ctx):
		return await checks.requires_channel_tag("game")(ctx)

	@commands.group(name="test", help="Pet System")
	async def test(self, ctx: commands.Context):
		if ctx.invoked_subcommand is None:
			return await ctx.send_help(ctx.command)

	@commands.command(name="pet", aliases=["p"], help="Display your pet stats")
	async def pet(self, ctx: commands.Context):
		with FileReader("pet_stats.json") as file:
			pet_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)

		stats_text = (
			f":heart: {pet_stats['health']:,}\n"
			f":crossed_swords: {pet_stats['attack']:,}\n"
			f":shield: {pet_stats['defence']:,}"
		)

		desc = f"{pet_stats['name']} | Lvl: {functions.pet_level_from_xp(pet_stats)}"
		embed = functions.create_embed(ctx.author.display_name, desc, ctx.author.avatar_url)
		embed.add_field(name="Stats", value=stats_text)

		await ctx.send(embed=embed)

	@commands.command(name="setname", help="Set name of pet")
	async def set_name(self, ctx: commands.Context, new_pet_name: str):
		with FileReader("pet_stats.json") as pet_stats:
			pet_stats.set_inner_key(str(ctx.author.id), "name", new_pet_name)

		await ctx.send(f"**{ctx.author.display_name}** has renamed their pet to **{new_pet_name}**")

	@commands.cooldown(1, 60, commands.BucketType.user)
	@commands.command(name="fight", help="Attack! [60s]")
	async def fight(self, ctx: commands.Context, defender: converters.ValidUser()):
		def wait_for_react(react, user_):
			return user_.id == ctx.author.id and react.emoji in self.ATTACK_REACTIONS

		# Load stats
		with FileReader("pet_stats.json") as file:
			author_stats = file.get(str(ctx.author.id), self.DEFAULT_STATS)
			target_stats = file.get(str(defender.id), self.DEFAULT_STATS)

		message = await self.create_pet_attack_menu(ctx, author_stats, target_stats)

		embed = message.embeds[0]

		# - - - WAIT FOR USER INPUT - - -
		try:
			await self.bot.wait_for("reaction_add", timeout=60, check=wait_for_react)
		except asyncio.TimeoutError:
			embed.set_field_at(0, name="Battle Report", value="Timed out")

			return await message.edit(embed=embed)
		# - - -

		message = discord.utils.get(self.bot.cached_messages, id=message.id)

		attack_index = await functions.get_reaction_index(ctx.author, message)
		fight_rewards = await self.perform_pet_attack(attack_index, ctx.author, defender)

		battle_report = (
			f":heart: {fight_rewards['health']}\n"
			f":moneybag: {fight_rewards['coins']}\n"
			f":star: {fight_rewards['xp']}"
		)

		embed.set_field_at(0, name="Battle Report", value=battle_report)
		embed.set_footer(text="Darkness")

		await message.edit(embed=embed)

	async def create_pet_attack_menu(self, ctx: commands.Context, attacker: dict, defender: dict) -> discord.Message:
		description = f"**'{attacker['name']}'** vs **'{defender['name']}'**"

		# - - - Create Embed - - -
		embed = discord.Embed(title="Pet Battle", color=0xff8000, description=description)

		embed.set_thumbnail(url=ctx.author.avatar_url)

		embed.add_field(name="How to Play", value="Select a reaction")
		# - - -

		msg = await ctx.send(embed=embed)

		for emoji in self.ATTACK_REACTIONS:
			await msg.add_reaction(emoji)

		return msg

	async def perform_pet_attack(self, attack: int, attacker: discord.Member, defender: discord.Member):
		with FileReader("pet_stats.json") as file:
			_ = file.get(str(attacker.id), self.DEFAULT_STATS)
			_ = file.get(str(defender.id), self.DEFAULT_STATS)

		return {"health": 0, "coins": 0, "xp": 0}

	@commands.command(name="petlb", aliases=["plb"], help="Show the pet leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		leaderboard_string = await self._leaderboard.create(ctx.author)

		await ctx.send(leaderboard_string)









