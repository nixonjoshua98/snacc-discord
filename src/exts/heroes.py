from pymongo import UpdateOne

from discord.ext import commands

from src import utils

from src.structs.confirm import Confirm
from src.structs.displaypages import DisplayPages

from src.common.heroes import HeroChests, ChestHeroes
from src.common.converters import HeroFromChest, Range


class Heroes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(name="heroes", aliases=["hero", "h"], invoke_without_command=True)
	async def show_heroes(self, ctx):
		""" View your owned heroes. """

		heroes = await ctx.bot.db["heroes"].find(
			{"user": ctx.author.id, "owned": {"$gt": 0}}
		).sort("hero", 1).to_list(length=None)

		if not heroes:
			return await ctx.send("You do not currently own any heroes.")

		embeds, chunks = [], [heroes[i:i + 9] for i in range(0, len(heroes), 9)]

		for i, chunk in enumerate(chunks):
			embed = ctx.bot.embed(title=f"Your Heroes [Page {i + 1}/{len(chunks)}]", author=ctx.author)

			embed.description = f"**Collected: {len(heroes)}/{len(ChestHeroes.ALL_HEROES)}**"

			embeds.append(embed)

			for hero in chunk:
				hero_inst = ChestHeroes.get(id=hero["hero"])

				hero_level = utils.hero_xp_to_level(hero.get("xp", 0))

				name = f"#{hero_inst.id:02d} | [{hero_inst.grade}] {hero_inst.name}"

				embed.add_field(name=name, value=f"Owned {hero['owned']} | Level {hero_level}")

		await DisplayPages(embeds).send(ctx)

	@show_heroes.command(name="chest")
	@commands.has_permissions(add_reactions=True)
	async def hero_chests(self, ctx, amount: Range(1, 5) = 1):
		""" Open a hero chest. """

		chest = HeroChests.get(id=0)

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

		if hero_entry is None or hero_entry.get("owned", 0) + 1 < amount:
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


def setup(bot):
	bot.add_cog(Heroes(bot))
