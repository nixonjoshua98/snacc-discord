import math
import random
import itertools

import datetime as dt

from discord.ext import commands

from src import inputs

from src.common import checks
from src.common.converters import EmpireQuest

from src.data import EmpireQuests, MilitaryGroup


class Quests(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	def get_max_quests(upgrades):
		return 1 + upgrades.get("quest_slots", 0)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="quest", aliases=["q"], invoke_without_command=True)
	async def quest_group(self, ctx, quest: EmpireQuest()):
		""" Embark on a new quest. """

		# - Query the database
		quests = await ctx.bot.mongo.find("quests", {"user": ctx.author.id}).to_list(length=100)

		upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})
		military = await ctx.bot.mongo.find_one("military", {"_id": ctx.author.id})

		if len(quests) < self.get_max_quests(upgrades):
			power = MilitaryGroup.get_total_power(military)

			duration = dt.timedelta(hours=quest.get_duration(upgrades))

			sucess_rate = quest.success_rate(power)

			row = dict(user=ctx.author.id, quest=quest.id, success_rate=sucess_rate, start=dt.datetime.utcnow())

			await ctx.bot.mongo.insert_one("quests", row)

			await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{duration}**")

		else:
			await ctx.send("You have already embarked on your maximum number of quests.")

	@checks.has_empire()
	@commands.command(name="quests")
	async def quests(self, ctx):
		""" Show all of the available quests to embark on. """

		# - Query the database
		upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})
		military = await ctx.bot.mongo.find_one("military", {"_id": ctx.author.id})

		power = MilitaryGroup.get_total_power(military)

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

		await inputs.send_pages(ctx, embeds)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="status")
	async def status(self, ctx):
		""" Show the status of your current quests and collect your rewards from your completed quests. """

		# - Query the database
		quests = await ctx.bot.mongo.find("quests", {"user": ctx.author.id}).to_list(length=100)
		upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

		embed = ctx.bot.embed(title=f"Ongoing Quests {len(quests)}/{self.get_max_quests(upgrades)}")

		for quest in quests:
			inst = EmpireQuests.get(id=quest["quest"])

			duration = inst.get_duration(upgrades)

			time_since_start = dt.datetime.utcnow() - quest["start"]

			# - Quest has ended
			if (time_since_start.total_seconds() / 3600) >= duration:
				upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

				quest_completed = quest["success_rate"] >= random.uniform(0.0, 1.0)

				money_reward = inst.get_reward(upgrades)

				if quest_completed:
					await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": money_reward})

					embed.add_field(name=f"[Completed] {inst.name}", value=f"`Reward: ${money_reward}`")

				else:
					embed.add_field(name=f"[Failed] {inst.name}", value="None")

				await ctx.bot.mongo.delete_one("quests", {"_id": quest["_id"]})

			else:
				timedelta = dt.timedelta(seconds=int(duration * 3_600 - time_since_start.total_seconds()))

				embed.add_field(name=inst.name, value=f"`{timedelta}`")

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Quests(bot))
