import math
import random

import datetime as dt

from discord.ext import commands

from src import inputs

from src.common import checks
from src.common.converters import EmpireQuest
from src.common.models import PopulationM, BankM, UserUpgradesM

from src.data import EmpireQuests, MilitaryGroup


class Quest(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	def get_max_quests(upgrades):
		return 1 + upgrades.get("extra_quests", 0)

	async def get_current_quests_embed(self, ctx, quests, upgrades):
		max_num_quests = self.get_max_quests(upgrades)

		embed = ctx.bot.embed(title=f"Ongoing Quests {len(quests)}/{max_num_quests}", thumbnail=ctx.author.avatar_url)

		for quest in quests:
			inst = EmpireQuests.get(id=quest["quest"])

			time_since_start = dt.datetime.utcnow() - quest["start"]

			seconds = inst.get_duration(upgrades) * 3_600 - time_since_start.total_seconds()

			timedelta = dt.timedelta(seconds=int(seconds))

			embed.add_field(name=inst.name, value=f"`{timedelta}`")

		return embed

	async def show_all_quests(self, ctx, quests, upgrades):
		population = await PopulationM.fetchrow(ctx.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(population)

		embeds = [await self.get_current_quests_embed(ctx, quests, upgrades)]

		for quest in EmpireQuests.quests:
			embed = ctx.bot.embed(title=f"Quest {quest.id}: {quest.name}", thumbnail=ctx.author.avatar_url)

			sucess_rate = quest.success_rate(author_power)

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

	@staticmethod
	async def complete_quest_and_get_embed(ctx, quest):
		quest_inst = EmpireQuests.get(id=quest["quest"])

		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		quest_completed = quest["success_rate"] >= random.uniform(0.0, 1.0)

		embed = ctx.bot.embed(title="Quest Completion!" if quest_completed else "Quest Failed!")

		if quest_completed:
			money_reward = quest_inst.get_reward(upgrades)

			await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=money_reward)

			embed.add_field(name=quest_inst.name, value=f"**Reward:** ${money_reward}")

		await ctx.bot.mongo.delete_one("quests", {"_id": quest["_id"]})

		return embed

	@checks.has_empire()
	@commands.command(name="quest_", aliases=["q"], invoke_without_command=True, usage="<quest=None>")
	async def quest_group(self, ctx, quest: EmpireQuest() = None):
		"""
*One quest can be ongoing at any one time*

- `!q` will show all quests or complete your previous quest
- `!q 5` while on a quest will do the same as `!q`
- `!q 5` while not on a quest will start a new quest
		"""

		current_quests = await ctx.bot.mongo.find("quests", {"user": ctx.author.id}).to_list(length=100)

		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		max_num_quests = self.get_max_quests(upgrades)

		if len(current_quests) < max_num_quests:

			# - Start a new quest
			if quest is not None:
				population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

				power = MilitaryGroup.get_total_power(population)
				duration = dt.timedelta(hours=quest.get_duration(upgrades))
				sucess_rate = quest.success_rate(power)

				row = dict(user=ctx.author.id, quest=quest.id, sucess_rate=sucess_rate, start=dt.datetime.utcnow())

				await ctx.bot.mongo.insert_one("quests", row)

				return await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{duration}**")

			return await self.show_all_quests(ctx, current_quests, upgrades)

		else:
			quest_embeds = []

			for quest in current_quests:
				inst = EmpireQuests.get(id=quest["quest"])

				duration = inst.get_duration(upgrades)

				time_since_start = dt.datetime.utcnow() - quest["start"]

				# - Quest completed
				if (time_since_start.total_seconds() / 3600) >= duration:
					embed = await self.complete_quest_and_get_embed(ctx, quest)

					quest_embeds.append(embed)

			if quest_embeds:
				return await inputs.send_pages(ctx, quest_embeds)

			await self.show_all_quests(ctx, current_quests, upgrades)


def setup(bot):
	bot.add_cog(Quest(bot))
