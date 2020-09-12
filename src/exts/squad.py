import math
import random

from discord.ext import commands

from pymongo import UpdateOne

import datetime as dt

from src import utils

from src.common import checks, HeroValues

from src.common.heroes import ChestHeroes
from src.common.converters import HeroFromChest


class Squad(commands.Cog):

	@checks.has_empire()
	@commands.group(name="squad", invoke_without_command=True)
	async def show_squad(self, ctx):
		""" Show your hero squad. """

		squad = await ctx.bot.db["heroes"].find(
			{"user": ctx.author.id, "in_squad": True}
		).sort("hero", 1).to_list(length=None)

		embed = ctx.bot.embed(title="Hero Squad", author=ctx.author)

		for hero in squad:
			hero_inst = ChestHeroes.get(id=hero["hero"])

			hero_level = utils.hero_xp_to_level(hero.get("xp", 0))

			name = f"#{hero_inst.id:02d} [{hero_inst.grade}] {hero_inst.name: <20}"

			embed.add_field(name=name, value=f"Level {hero_level}", inline=False)

		await ctx.send(embed=embed)

	@checks.has_empire()
	@checks.hero_squad_not_training()
	@show_squad.command(name="add")
	async def add_to_squad(self, ctx, hero: HeroFromChest()):
		""" Add a new hero to your squad. """

		squad = await ctx.bot.db["heroes"].find(
			{"user": ctx.author.id, "in_squad": True}
		).sort("hero", 1).to_list(length=None)

		hero_row = await ctx.bot.db["heroes"].find_one({"user": ctx.author.id, "hero": hero.id})

		squad_ids = [h["hero"] for h in squad]

		if hero.id in squad_ids:
			return await ctx.send(f"Hero **#{hero.id}** is already in your squad")

		elif hero_row is None or hero_row.get("owned", 0) == 0:
			return await ctx.send(f"You do not own hero **#{hero.id}**")

		elif len(squad) >= HeroValues.SQUAD_SIZE:
			return await ctx.send(f"Your squad is already full. Remove a hero first")

		# - Add the hero to the author's squad
		await ctx.bot.db["heroes"].update_one(
			{"user": ctx.author.id, "hero": hero.id},
			{"$set": {"in_squad": True}},
			upsert=True
		)

		await ctx.send(f"Hero **#{hero.id} {hero.name}** has been added to your squad.")

	@checks.has_empire()
	@checks.hero_squad_not_training()
	@show_squad.command(name="rmv", aliases=["rm", "del"])
	async def remove_from_squad(self, ctx, hero: HeroFromChest()):
		""" Remove a new hero to your squad. """

		squad = await ctx.bot.db["heroes"].find(
			{"user": ctx.author.id, "in_squad": True}
		).sort("hero", 1).to_list(length=None)

		squad_ids = [h["hero"] for h in squad]

		if hero.id not in squad_ids:
			return await ctx.send(f"Hero **#{hero.id}** is not in your squad")

		# - Remove the hero from the author's squad
		await ctx.bot.db["heroes"].update_one(
			{"user": ctx.author.id, "hero": hero.id},
			{"$unset": {"in_squad": None}},
			upsert=True
		)

		await ctx.send(f"Hero **#{hero.id} {hero.name}** has been removed from your squad.")

	@checks.has_empire()
	@checks.has_hero_squad()
	@commands.cooldown(1, 300, commands.BucketType.user)
	@show_squad.command(name="train")
	async def start_training(self, ctx):
		""" Start or stop your squad training. """

		squad = await ctx.bot.db["heroes"].find(
			{"user": ctx.author.id, "in_squad": True}
		).sort("hero", 1).to_list(length=None)

		training_row = await ctx.bot.db["hero_training"].find_one({"_id": ctx.author.id})

		if training_row is None:
			await ctx.bot.db["hero_training"].insert_one({"_id": ctx.author.id, "start": dt.datetime.utcnow()})

			await ctx.send(f"Your squad has started training. Check back later")

		else:
			training_dur = min(8, (dt.datetime.utcnow() - training_row["start"]).total_seconds() / 3600)

			embed = ctx.bot.embed(title="Training", author=ctx.author)

			requests = []

			for hero in squad:
				hero_inst = ChestHeroes.get(id=hero["hero"])

				name = f"#{hero_inst.id} {hero_inst.name}"

				xp_gained = math.floor(random.randint(50, 100) * training_dur)

				old_level = utils.hero_xp_to_level(hero.get("xp", 0))
				new_level = utils.hero_xp_to_level(hero.get("xp", 0) + xp_gained)

				value = f"Gained **{xp_gained:,} XP**"

				r = UpdateOne({"user": ctx.author.id, "hero": hero["hero"]}, {"$inc": {"xp": xp_gained}}, upsert=True)

				if new_level > old_level:
					value = f"Gained **{xp_gained:,} XP** and levelled up **{old_level} -> {new_level}**"

				requests.append(r)

				embed.add_field(name=name, value=value, inline=False)

			await ctx.bot.db["heroes"].bulk_write(requests)

			await ctx.bot.db["hero_training"].delete_one({"_id": ctx.author.id})

			await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Squad(bot))
