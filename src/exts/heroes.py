import itertools

from pymongo import UpdateOne

from discord.ext import commands

from src.structs.confirm import Confirm
from src.structs.displaypages import DisplayPages

from src.common.heroes import HeroChests, ChestHeroes
from src.common.converters import HeroFromChest, Range, ValidHeroChest


class Heroes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(name="heroes", aliases=["h"], invoke_without_command=True)
	async def show_heroes(self, ctx):
		""" View your owned heroes. """

		heroes = await ctx.bot.db["heroes"].find(
			{"user": ctx.author.id, "owned": {"$gt": 0}}
		).sort("hero", 1).to_list(length=None)

		if not heroes:
			return await ctx.send("You do not currently own any heroes.")

		embeds, chunks = [], [heroes[i:i + 8] for i in range(0, len(heroes), 8)]

		# - Initial Embed
		embed = ctx.bot.embed(title=f"Your Hero Collection", author=ctx.author)

		desc = [f"**Collected: {len(heroes)}/{len(ChestHeroes.ALL_HEROES)}**\n"]

		for grade in ChestHeroes.ALL_GRADES:
			num_heroes = len([h for h in ChestHeroes.ALL_HEROES if h.grade == grade])

			num_owned_heroes = len([row for row in heroes if ChestHeroes.get(id=row["hero"]).grade == grade])

			desc.append(f"`{grade} {f'{num_owned_heroes}/{num_heroes:}': <6}`")

		embed.description = "\n".join(desc)

		embeds.append(embed)
		# -

		for i, chunk in enumerate(chunks):
			embed = ctx.bot.embed(title=f"Your Heroes [Page {i + 1}/{len(chunks)}]", author=ctx.author)

			embeds.append(embed)

			for j, hero in enumerate(chunk, start=1):
				hero_inst = ChestHeroes.get(id=hero["hero"])

				hero_level = hero_inst.xp_to_level(hero.get("xp", 0))

				name = f"#{hero_inst.id:02d} | [{hero_inst.grade}] {hero_inst.name}"

				value = (
					f"Owned {hero['owned']} | Level {hero_level} | "
					f"ATK {hero_inst.get_atk(hero)} | HP {hero_inst.get_hp(hero)}"
				)

				embed.add_field(name=name, value=value, inline=False)

		await DisplayPages(embeds).send(ctx)

	@show_heroes.command(name="chest")
	@commands.has_permissions(add_reactions=True)
	async def hero_chests(self, ctx, chest: ValidHeroChest(), amount: Range(1, 10) = 1):
		""" Open a hero chest. """

		cost = chest.cost * amount

		desc = f"Buy and open **{amount:,}x {chest.name}** for **${cost:,}**?"

		embed = ctx.bot.embed(title="Hero Chests", description=desc, author=ctx.author)

		if not await Confirm(embed).prompt(ctx):
			return await ctx.send("Hero chest purchase aborted.")

		bank = await ctx.bot.db["bank"].find_one({"_id": ctx.author.id})

		# - Check if the author can afford the crate
		if bank is None or bank.get("usd", 0) < cost:
			return await ctx.send(f"You cannot afford **{amount:,}x {chest.name}**.")

		await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": -cost}})

		new_heroes = chest.open(amount)

		desc, requests = [], []

		embed = ctx.bot.embed(title=chest.name, description=desc, author=ctx.author)

		for hero, opened in new_heroes.items():
			requests.append(UpdateOne({"user": ctx.author.id, "hero": hero.id}, {"$inc": {"owned": 1}}, upsert=True))

			desc.append(f"You pulled **{opened}x #{hero.id:02d} {hero.name} [{hero.grade}]**")

		embed.description = "\n".join(desc)

		await ctx.bot.db["heroes"].bulk_write(requests)

		await ctx.send(embed=embed)

	@show_heroes.command(name="sell")
	async def sell_hero(self, ctx, hero: HeroFromChest(), amount: Range(1, None) = 1):
		""" Sell your heroes. """

		hero_entry = await ctx.bot.db["heroes"].find_one({"user": ctx.author.id, "hero": hero.id})

		if hero_entry is None or hero_entry.get("owned", 0) < amount + 1:
			await ctx.send(f"You do not have **{amount:,}x** duplicates of **#{hero.id}** available to sell")

		else:
			money = hero.sell_price * amount

			if await Confirm(f"Sell **{amount:,}x** hero **#{hero.id}** for **${money:,}**?").prompt(ctx):

				await ctx.bot.db["heroes"].update_one(
					{"user": ctx.author.id, "hero": hero.id},
					{"$inc": {"owned": -amount}}
				)

				await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": money}})

				await ctx.send(f"Sold **{amount:,}x** hero **#{hero.id}** for **${money:,}**")

			else:
				await ctx.send("Hero sale aborted")

	@show_heroes.command(name="chests")
	async def show_chests(self, ctx):
		""" Show information about each hero chest. """

		embed = ctx.bot.embed(title="Hero Chests")

		for chest in HeroChests.ALL:
			full_weight = sum([hero.weight for hero in chest.all])

			value = []

			for grade, heroes in itertools.groupby(chest.all, lambda h: h.grade):
				heroes = list(heroes)

				total_weight = sum([h.weight for h in heroes])

				value.append(f"{grade} {round((total_weight / full_weight) * 100, 1)}%")

			name = f"{chest.id} | {chest.name} [${chest.cost:,}]"

			embed.add_field(name=name, value=f"`{' '.join(value)}`", inline=False)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Heroes(bot))
