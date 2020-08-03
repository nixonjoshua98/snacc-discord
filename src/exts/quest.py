import math
import random

import datetime as dt

from discord.ext import commands

from src import inputs

from src.common import checks
from src.common.converters import EmpireQuest
from src.common.models import QuestsM, PopulationM, BankM

from src.common.empireunits import MilitaryGroup
from src.common.empirequests import EmpireQuests


class Quest(commands.Cog):
	@checks.has_empire()
	@commands.group(name="quest", aliases=["q"], invoke_without_command=True)
	async def quest_group(self, ctx):
		""" Display all the available quests. """

		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(author_population)

		embeds = []

		for quest in EmpireQuests.quests:
			embed = ctx.bot.embed(title=f"Quest {quest.id}: {quest.name}", thumbnail=ctx.author.avatar_url)

			sucess_rate = quest.success_rate(author_power)

			embed.description = "\n".join(
				[
					f"**Duration:** {quest.duration} hour(s)",
					f"**Success Rate:** {math.floor(sucess_rate * 100)}%",
					f"**Avg. Reward:** ${quest.reward:,}"
				]
			)

			embeds.append(embed)

		await inputs.send_pages(ctx, embeds)

	@checks.has_empire()
	@quest_group.command(name="current", aliases=["c"])
	async def current_quest(self, ctx):
		""" Display the quest which you are currently embarked on. """

		quest = await QuestsM.fetchrow(ctx.bot.pool, ctx.author.id, insert=False)

		if quest is None:
			await ctx.send("You are not currently on a quest.")

		else:
			time_since_start = dt.datetime.utcnow() - quest["date_started"]

			quest_inst = EmpireQuests.get(id=quest["quest_num"])

			if (time_since_start.total_seconds() / 3600) > quest_inst.duration:
				await QuestsM.delete(ctx.bot.pool, ctx.author.id)

				# - User completed the quest without dying
				if quest["success_rate"] >= random.uniform(0.0, 1.0):
					money_reward = quest_inst.get_reward()

					await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=money_reward)

					embed = ctx.bot.embed(title="Quest Completion!")

					value = [f"**Reward:** ${money_reward}", f"**Duration:** {quest_inst.duration} hour(s)"]

					embed.add_field(name=quest_inst.name, value="\n".join(value))

					await ctx.send(embed=embed)

				else:
					await ctx.send("Your squad died while questing!")

			else:
				seconds = quest_inst.duration * 3600 - time_since_start.total_seconds()

				await ctx.send(f"Your current quest will conclude in `{dt.timedelta(seconds=int(seconds))}`")

	@checks.has_empire()
	@checks.not_on_quest()
	@quest_group.command(name="start", aliases=["s"])
	async def start_quest(self, ctx, quest: EmpireQuest()):
		""" Start a new quest. """

		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(author_population)

		sucess_rate = quest.success_rate(author_power)

		await ctx.bot.pool.execute(QuestsM.INSERT_ROW, ctx.author.id, quest.id, sucess_rate, dt.datetime.utcnow())

		await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{quest.duration}** hour(s)")


def setup(bot):
	bot.add_cog(Quest())
