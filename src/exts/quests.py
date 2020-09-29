import math
import random

from pymongo import InsertOne

import datetime as dt

from discord.ext import commands

from src.common import checks
from src.common.quests import EmpireQuests
from src.common.population import Military
from src.common.converters import EmpireQuest

from src.structs.displaypages import DisplayPages


class Quests(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="quest", aliases=["q"], invoke_without_command=True)
	async def quest_group(self, ctx, quest: EmpireQuest()):
		""" Embark on a new quest. """

		current_quest = await ctx.bot.db["quests"].find_one({"_id": ctx.author.id})

		if current_quest is None:
			empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

			upgrades = empire.get("upgrades", dict())

			empire_power = Military.calc_total_power(empire)

			duration = dt.timedelta(hours=quest.get_duration(upgrades))

			sucess_rate = quest.success_rate(empire_power)

			row = dict(_id=ctx.author.id, quest=quest.id, success_rate=sucess_rate, start=dt.datetime.utcnow())

			await ctx.bot.db["quests"].insert_one(row)

			await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{duration}**")

		else:
			await self.show_status(ctx)

	@checks.has_empire()
	@commands.command(name="quests")
	async def quests(self, ctx):
		""" Show all of the available quests to embark on. """

		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		upgrades = empire.get("upgrades", dict())

		power = Military.calc_total_power(empire)

		embeds = []

		for quest in EmpireQuests.quests:
			embed = ctx.bot.embed(title=f"Quest {quest.id}: {quest.name}")

			sucess_rate = quest.success_rate(power)

			duration = dt.timedelta(hours=quest.get_duration(upgrades))

			embed.description = "\n".join(
				[
					f"**Duration:** {duration}",
					f"**Success Rate:** {math.floor(sucess_rate * 100)}%",
					f"**Avg. Reward:** ${quest.get_avg_reward(upgrades):,}"
				]
			)

			embeds.append(embed)

		await DisplayPages(embeds).send(ctx)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="status")
	async def show_status(self, ctx):
		""" Show the status of your current quest. """

		current_quest = await ctx.bot.db["quests"].find_one({"_id": ctx.author.id})

		# - User is not on a quest
		if current_quest is None:
			return await ctx.send("You are not currently embarked on a quest.")

		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		upgrades = empire.get("upgrades", dict())

		quest_instance = EmpireQuests.get(id=current_quest["quest"])

		embed = ctx.bot.embed(title=quest_instance.name)

		quest_duration = quest_instance.get_duration(upgrades)

		time_since_start = dt.datetime.utcnow() - current_quest["start"]

		# - Quest has ended
		if (time_since_start.total_seconds() / 3600) >= quest_duration:

			await ctx.bot.db["quests"].delete_one({"_id": ctx.author.id})

			# = Quest success
			if current_quest["success_rate"] >= random.uniform(0.0, 1.0):

				reward = quest_instance.get_reward(upgrades)

				# - Add the reward money to the account
				await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": reward}}, upsert=True)

				loot = quest_instance.get_loot()

				embed.description = f"Quest completed!\nYou have been rewarded **${reward:,}**"

				if loot:
					requests, value = [], []

					for item_name, item_value in loot.items():
						requests.append(InsertOne({"user": ctx.author.id, "name": item_name, "value": item_value}))

						value.append(f"{item_name} **${item_value:,}**")

					await ctx.bot.db["loot"].bulk_write(requests)

					embed.add_field(name="Loot", value="\n".join(value))

			else:
				embed.description = "Your squad died while on the quest!"

		else:
			timedelta = dt.timedelta(seconds=int(quest_duration * 3_600 - time_since_start.total_seconds()))

			embed.add_field(name="Time", value=timedelta)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Quests(bot))
