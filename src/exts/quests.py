import math
import random

import datetime as dt

from discord.ext import commands

from src import inputs

from src.common import checks
from src.common.converters import EmpireQuest
from src.common.models import PopulationM, BankM, UserUpgradesM

from src.data import EmpireQuests, MilitaryGroup


class Quests(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	def get_max_quests(upgrades):
		return 1 + upgrades.get("quest_slots", 0)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="quest", aliases=["q"], invoke_without_command=True, usage="<quest=None>")
	async def quest_group(self, ctx, quest: EmpireQuest() = None):
		""" Embark on a new quest. """

		quests = await ctx.bot.mongo.find("quests", {"user": ctx.author.id}).to_list(length=100)

		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		max_num_quests = self.get_max_quests(upgrades)

		if len(quests) < max_num_quests:
			population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

			power = MilitaryGroup.get_total_power(population)

			duration = dt.timedelta(hours=quest.get_duration(upgrades))

			sucess_rate = quest.success_rate(power)

			row = dict(user=ctx.author.id, quest=quest.id, success_rate=sucess_rate, start=dt.datetime.utcnow())

			await ctx.bot.mongo.insert_one("quests", row)

			return await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{duration}**")

	@checks.has_empire()
	@commands.command(name="quests")
	async def quests(self, ctx):
		""" Show all of the available quests to embark on. """

		population = await PopulationM.fetchrow(ctx.pool, ctx.author.id)

		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		power = MilitaryGroup.get_total_power(population)

		embeds = []

		for quest in EmpireQuests.quests:
			embed = ctx.bot.embed(title=f"Quest {quest.id}: {quest.name}", thumbnail=ctx.author.avatar_url)

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

		quests = await ctx.bot.mongo.find("quests", {"user": ctx.author.id}).to_list(length=100)

		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		max_num_quests = self.get_max_quests(upgrades)

		embed = ctx.bot.embed(title=f"Ongoing Quests {len(quests)}/{max_num_quests}", thumbnail=ctx.author.avatar_url)

		for quest in quests:
			inst = EmpireQuests.get(id=quest["quest"])

			time_since_start = dt.datetime.utcnow() - quest["start"]

			seconds = inst.get_duration(upgrades) * 3_600 - time_since_start.total_seconds()

			inst = EmpireQuests.get(id=quest["quest"])

			duration = inst.get_duration(upgrades)

			time_since_start = dt.datetime.utcnow() - quest["start"]

			# - Quest has ended
			if (time_since_start.total_seconds() / 3600) >= duration:
				upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

				quest_completed = quest["success_rate"] >= random.uniform(0.0, 1.0)

				money_reward = inst.get_reward(upgrades)

				if quest_completed:
					await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=money_reward)

				embed.add_field(
					name=inst.name,
					value=f"`**Reward:** ${money_reward}`" if quest_completed else "`Quest Failed`"
				)

				await ctx.bot.mongo.delete_one("quests", {"_id": quest["_id"]})

			else:
				timedelta = dt.timedelta(seconds=int(seconds))

				embed.add_field(name=inst.name, value=f"`{timedelta}`")

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Quests(bot))
