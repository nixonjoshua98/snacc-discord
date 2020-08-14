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

	async def get_quest_timer(self, user, *, upgrades=None):
		current_quest = await self.bot.mongo.find_one("quests", {"user": user.id})

		if current_quest is None:
			return None

		author_upgrades = upgrades if upgrades is not None else await UserUpgradesM.fetchrow(con, user.id)

		quest_inst = EmpireQuests.get(id=current_quest["quest"])

		time_since_start = dt.datetime.utcnow() - current_quest["start"]

		seconds = quest_inst.get_duration(author_upgrades) * 3600 - time_since_start.total_seconds()

		return dt.timedelta(seconds=int(seconds))

	async def show_all_quests(self, ctx):
		async with ctx.pool.acquire() as con:
			author_population = await PopulationM.fetchrow(con, ctx.author.id)
			author_upgrades = await UserUpgradesM.fetchrow(con, ctx.author.id)

		author_power = MilitaryGroup.get_total_power(author_population)

		embeds = []

		timer = await self.get_quest_timer(ctx.author, upgrades=author_upgrades)

		quest_text = timer if timer is None or timer.total_seconds() > 0 else 'Finished'

		for quest in EmpireQuests.quests:
			embed = ctx.bot.embed(title=f"Quest {quest.id}: {quest.name}", thumbnail=ctx.author.avatar_url)

			sucess_rate = quest.success_rate(author_power)

			duration = dt.timedelta(hours=quest.get_duration(author_upgrades))

			embed.description = "\n".join(
				[
					f"*Current Quest: {quest_text}*"
					f"\n",
					f"**Duration:** {duration}",
					f"**Success Rate:** {math.floor(sucess_rate * 100)}%",
					f"**Avg. Reward:** ${quest.get_avg_reward(author_upgrades):,}"
				]
			)

			embeds.append(embed)

		await inputs.send_pages(ctx, embeds)

	@staticmethod
	async def complete_quest(ctx, quest):
		quest_inst = EmpireQuests.get(id=quest["quest"])

		await ctx.bot.mongo.delete_one("quests", {"user": ctx.author.id})

		# - User completed the quest without dying
		if quest["success_rate"] >= random.uniform(0.0, 1.0):
			author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

			money_reward = quest_inst.get_reward(author_upgrades)

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

		row = dict(user=ctx.author.id, quest=quest.id, sucess_rate=sucess_rate, start=dt.datetime.utcnow())

		await ctx.bot.mongo.insert_one("quests", row)

		await ctx.send(f"You have embarked on **- {quest.name} -** quest! Check back in **{duration}**")

	@checks.has_empire()
	@commands.command(name="quest", aliases=["q"], invoke_without_command=True, usage="<quest=None>")
	async def quest_group(self, ctx, quest: EmpireQuest() = None):
		"""
*One quest can be ongoing at any one time*

- `!q` will show all quests or complete your previous quest
- `!q 5` while on a quest will do the same as `!q`
- `!q 5` while not on a quest will start a new quest
		"""

		current_quest = await ctx.bot.mongo.find_one("quests", {"user": ctx.author.id})

		if current_quest is None:
			if quest is not None:
				return await self.start_quest(ctx, quest)

			return await self.show_all_quests(ctx)

		author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)

		quest_inst = EmpireQuests.get(id=current_quest["quest"])

		time_since_start = dt.datetime.utcnow() - current_quest["start"]

		if (time_since_start.total_seconds() / 3600) >= quest_inst.get_duration(author_upgrades):
			return await self.complete_quest(ctx, current_quest)

		await self.show_all_quests(ctx)


def setup(bot):
	bot.add_cog(Quest(bot))
