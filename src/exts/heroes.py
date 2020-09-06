import math

from src.common.heroes import HeroChests, ChestHeroes

from src.structs.confirm import Confirm

from src.common.converters import HeroFromChest, Range

from discord.ext import commands


class Heroes(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.group(name="heroes", aliases=["h"], invoke_without_command=True)
	async def show_heroes(self, ctx):
		""" View your owned heroes. """

		heroes = await ctx.bot.db["heroes"].find({"user": ctx.author.id, "owned": {"$gt": 0}}).to_list(length=None)

		heroes.sort(key=lambda h: h["hero"])

		embed = ctx.bot.embed(title="Your Heroes", author=ctx.author)

		desc = []

		for hero in heroes:
			hero_inst = ChestHeroes.get(id=hero["hero"])

			s = f"`#{hero_inst.id:02d} | {hero['owned']:02d}x [{hero_inst.grade}] {hero_inst.name: <16}`"

			desc.append(s)

		embed.description = "\n".join(desc)

		await ctx.send(embed=embed)

	@show_heroes.command(name="chest")
	@commands.has_permissions(add_reactions=True)
	@commands.cooldown(5, 1_800, commands.BucketType.user)
	async def hero_chests(self, ctx):
		""" Open a hero chest. """

		chest = HeroChests.get(id=0)

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

		desc = f"You pulled **#{hero.id:02d} {hero.name} [{hero.grade}]**"

		embed = ctx.bot.embed(title=chest.name, description=desc, author=ctx.author)

		if hero.icon is not None:
			embed.set_image(url=hero.icon)

		await ctx.send(embed=embed)

	@show_heroes.command(name="sell")
	async def sell_hero(self, ctx, hero: HeroFromChest(), amount: Range(1, None) = 1):
		""" Sell your heroes. """

		hero_entry = await ctx.bot.db["heroes"].find_one({"user": ctx.author.id, "hero": hero.id})

		if hero_entry is None or hero_entry.get("owned", 0) < amount:
			await ctx.send(f"You do not have **{amount:,}x** **#{hero.id}** available to sell")

		else:
			money = math.floor(hero.rating * 13.0) * amount

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
