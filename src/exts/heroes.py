
from src.common.heroes import HeroChests, ChestHeroes

from src.structs.confirm import Confirm

from discord.ext import commands


class Heroes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(name="heroes", invoke_without_command=True)
	async def show_heroes(self, ctx):
		""" View your owned heroes. """

		heroes = await ctx.bot.db["heroes"].find({"user": ctx.author.id}).to_list(length=None)

		embed = ctx.bot.embed(title="Your Heroes", author=ctx.author)

		for hero in heroes:
			hero_inst = ChestHeroes.get(id=hero["hero"])

			name = f"{hero_inst.name} | Owned {hero['owned']}"

			value = f"HP {hero_inst.base_health} | ATK {hero_inst.base_attack}"

			embed.add_field(name=name, value=value)

		await ctx.send(embed=embed)

	@show_heroes.command(name="chest")
	@commands.has_permissions(add_reactions=True)
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hero_chests(self, ctx):
		""" Open a hero chest. """

		chest = HeroChests.get(id=1)

		desc = f"Buy and open a **{chest.name}** for **${chest.cost:,}**?"

		embed = ctx.bot.embed(title="Hero Chests", description=desc, author=ctx.author)

		if not await Confirm(embed).prompt(ctx):
			return await ctx.send("Hero chest purchase aborted.")

		bank = await ctx.bot.db["bank"].find_one({"_id": ctx.author.id})

		# - Check if the author can afford the crate
		if bank is None or bank.get("usd", 0) < chest.cost:
			return await ctx.send(f"You cannot afford **{chest.name}**.")

		await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": -chest.cost}})

		hero = chest.open()

		await ctx.bot.db["heroes"].update_one(
			{"user": ctx.author.id, "hero": hero.id},
			{"$inc": {"owned": 1}},
			upsert=True
		)

		desc = f"You pulled **{hero.name}**!"

		embed = ctx.bot.embed(title=chest.name, description=desc, author=ctx.author, thumbnail=hero.icon)

		embed.add_field(
			name="Stats",
			value=(
				f"**HP:** {hero.base_health}\n"
				f"**ATK:**: {hero.base_attack}\n"
			)
		)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Heroes(bot))
