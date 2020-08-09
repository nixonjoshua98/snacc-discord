import math
import random

import datetime as dt

from discord.ext import commands

from src import inputs

from src.common import checks
from src.common.converters import EmpireQuest
from src.common.models import QuestsM, PopulationM, BankM, UserUpgradesM

from src.common.empireunits import MilitaryGroup
from src.common.empirequests import EmpireQuests


class Quest(commands.Cog):
	@staticmethod
	async def get_quest_timer(con, user):
		quest = await QuestsM.fetchrow(con, user.id, insert=False)

		if quest is None:
			return None

		author_upgrades = await UserUpgradesM.fetchrow(con, user.id)

		quest_inst = EmpireQuests.get(id=quest["quest_num"])

		time_since_start = dt.datetime.utcnow() - quest["date_started"]

		seconds = max(0, quest_inst.get_duration(author_upgrades) * 3600 - time_since_start.total_seconds())

		return dt.timedelta(seconds=int(seconds))

	@staticmethod
	async def show_all_quest(ctx):
		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(author_population)

		embeds = []

		for quest in EmpireQuests.quests:
			embed = ctx.bot.embed(title=f"Quest {quest.id}: {quest.name}", thumbnail=ctx.author.avatar_url)

			sucess_rate = quest.success_rate(author_power)

			duration = dt.timedelta(hours=quest.get_duration(author_upgrades))

			embed.description = "\n".join(
				[
					f"**Duration:** {duration}",
					f"**Success Rate:** {math.floor(sucess_rate * 100)}%",
					f"**Avg. Reward:** ${quest.reward:,}"
				]
			)

			embeds.append(embed)

		await inputs.send_pages(ctx, embeds)

	@staticmethod
	async def complete_quest(ctx, quest):
		quest_inst = EmpireQuests.get(id=quest["quest_num"])

		await QuestsM.delete(ctx.bot.pool, ctx.author.id)

		# - User completed the quest without dying
		if quest["success_rate"] >= random.uniform(0.0, 1.0):
			money_reward = quest_inst.get_reward()

			await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=money_reward)

			embed = ctx.bot.embed(title="Quest Completion!")

			embed.add_field(name=quest_inst.name, value=f"**Reward:** ${money_reward}")

			await ctx.send(embed=embed)

		else:
			await ctx.send("Your squad died while questing!")

	@staticmethod
	async def start_quest(ctx, quest):
		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)
		author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(author_population)

		sucess_rate = quest.success_rate(author_power)

		duration = dt.timedelta(hours=quest.get_duration(author_upgrades))

		await ctx.bot.pool.execute(QuestsM.INSERT_ROW, ctx.author.id, quest.id, sucess_rate, dt.datetime.utcnow())

		await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{duration}**")

	@checks.has_empire()
	@commands.group(name="quest", aliases=["q"], invoke_without_command=True, usage="<quest=None>")
	async def quest_group(self, ctx, quest: EmpireQuest() = None):
		"""
*One quest can be ongoing at any one time*

- `!q` will show all quests or complete your previous quest
- `!q 5` while on a quest will do the same as `!q`
- `!q 5` while not on a quest will start a new quest
		"""

		quest_row = await QuestsM.fetchrow(ctx.bot.pool, ctx.author.id, insert=False)

		if quest_row is None:
			if quest is not None:
				return await self.start_quest(ctx, quest)

			return await self.show_all_quest(ctx)

		author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		quest_inst = EmpireQuests.get(id=quest_row["quest_num"])

		time_since_start = dt.datetime.utcnow() - quest_row["date_started"]

		if (time_since_start.total_seconds() / 3600) >= quest_inst.get_duration(author_upgrades):
			return await self.complete_quest(ctx, quest_row)

		return await self.show_all_quest(ctx)


def setup(bot):
	bot.add_cog(Quest())
