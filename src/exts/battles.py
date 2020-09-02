
import random

from pymongo import UpdateOne

import datetime as dt

from src import utils

from discord.ext import commands

from src.common import checks
from src.common.population import Military

from src.common.converters import EmpireAttackTarget, DiscordUser, AnyoneWithEmpire


THIEF_UNIT = Military.get(key="thief")
SCOUT_UNIT = Military.get(key="scout")


class Battles(commands.Cog):

	@staticmethod
	def calc_win_chance(atk_power, def_power):
		return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))

	@staticmethod
	async def calc_units_lost(empire):
		units_lost = dict()
		units_lost_cost = 0

		hourly_income = max(0, utils.net_income(empire))

		units = empire.get("units", dict())

		# - Get available units
		avail_units = []
		for u in Military.units:
			unit_entry = units.get(u.key, dict())

			if unit_entry.get("owned", 0) > 0:
				avail_units.append(u)

		avail_units.sort(key=lambda u: u.calc_price(units.get(u.key, dict()).get("owned", 0), 1), reverse=False)

		for unit in avail_units:
			unit_entry = units.get(unit.key, dict())

			owned = unit_entry.get("owned", 0)

			for i in range(1, owned + 1):
				price = unit.calc_price(owned - i, i)

				if (price + units_lost_cost) < hourly_income:
					units_lost[unit] = i

				units_lost_cost = sum([unit.calc_price(owned - n, n) for u, n in units_lost.items()])

		return units_lost

	@checks.has_unit(SCOUT_UNIT, 1)
	@commands.cooldown(1, 15, commands.BucketType.user)
	@commands.command(name="scout", cooldown_after_parsing=True)
	async def scout(self, ctx, *, target: AnyoneWithEmpire()):
		""" Send a scout to a rival empire to search for information """

		author_empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id}) or dict()
		target_empire = await ctx.bot.db["empires"].find_one({"_id": target.id}) or dict()

		author_power = Military.calc_total_power(author_empire)
		target_power = Military.calc_total_power(target_empire)

		win_chance = self.calc_win_chance(author_power, target_power)

		await ctx.send(
			f"Your scout reports that you have a **{int(win_chance * 100)}%** "
			f"chance of winning against **{str(target)}**."
		)

	@checks.has_unit(THIEF_UNIT, 1)
	@commands.cooldown(1, 3_600, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal(self, ctx, *, target: DiscordUser()):
		""" Attempt to steal from another user. """

		def calculate_money_lost(bank):
			min_val, max_val = int(bank.get("usd", 0) * 0.015), int(bank.get("usd", 0) * 0.025)

			return random.randint(max(1, min_val), max(1, max_val))

		target_bank = await ctx.bot.db["bank"].find_one({"_id": target.id}) or dict()

		stolen_amount = calculate_money_lost(target_bank)

		thief_tax = int(stolen_amount // random.uniform(2.0, 6.0)) if stolen_amount >= 3_000 else 0

		await ctx.bot.db["bank"].bulk_write(
			[
				UpdateOne({"_id": ctx.author.id}, {"$inc": {"usd": stolen_amount - thief_tax}}, upsert=True),
				UpdateOne({"_id": target.id}, {"$inc": {"usd": -stolen_amount}}, upsert=True)
			]
		)

		s = f"You stole **${stolen_amount:,}** from **{target.display_name}!**"

		if thief_tax > 0:
			s = (
				f"You stole **${stolen_amount:,}** from **{target.display_name}!** "
				f"but the thief you hired took a cut of **${thief_tax:,}**."
			)

		await ctx.send(s)

	@checks.has_power(25)
	@commands.cooldown(1, 60 * 120, commands.BucketType.user)
	@commands.command(name="attack", cooldown_after_parsing=True)
	async def attack(self, ctx, *, target: EmpireAttackTarget()):
		""" Attack a rival empire. """

		def calc_pillaged_amount(empire, bank, multiplier: int = 1.0):
			hourly_income = max(0, utils.net_income(empire))

			min_val = max(0, int(bank.get("usd", 0) * 0.025))
			max_val = max(0, int(bank.get("usd", 0) * 0.050))

			stolen_amount = int(min(bank.get("usd", 0), hourly_income, random.randint(min_val, max_val) * multiplier))

			# - Add a bonus pillage amount if the chance of winning is less than 50%
			bonus_money = int((stolen_amount * 2.0) * (1.0 - win_chance) if win_chance < 0.50 else 0)

			return stolen_amount, bonus_money

		author_empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id}) or dict()
		target_empire = await ctx.bot.db["empires"].find_one({"_id": target.id}) or dict()

		author_power = Military.calc_total_power(author_empire)
		target_power = Military.calc_total_power(target_empire)

		win_chance = self.calc_win_chance(author_power, target_power)

		if win_chance >= random.uniform(0.0, 1.0):
			target_bank = await ctx.bot.db["bank"].find_one({"_id": target.id}) or dict()

			if units_lost := await self.calc_units_lost(target_empire):
				units_lost_keys = {f"units.{k.key}.owned": -v for k, v in units_lost.items()}

				await ctx.bot.db["empires"].update_one({"_id": target.id}, {"$inc": units_lost_keys}, upsert=True)

			pillaged, bonus = calc_pillaged_amount(target_empire, target_bank, 1.0 if units_lost else 2.0)

			await ctx.bot.db["bank"].bulk_write(
				[
					UpdateOne({"_id": ctx.author.id}, {"$inc": {"usd": pillaged + bonus}}, upsert=True),
					UpdateOne({"_id": target.id}, {"$inc": {"usd": (pillaged + bonus) * -1}}, upsert=True)
				]
			)

			await ctx.bot.db["empires"].update_one({"_id": target.id}, {"$set": {"last_attack": dt.datetime.utcnow()}})

			# - Create the message to return to Discord
			val = f"${pillaged:,} {f'**+ ${bonus:,} bonus**' if bonus > 0 else ''}"

			embed = ctx.bot.embed(
				title=target_empire.get('name', target.display_name),
				author=ctx.author,
				description=f"**Money Pillaged:** {val}"
			)

			if units_lost:
				units_lost_text = list(map(lambda kv: f"`{kv[1]}x {kv[0].display_name}`", units_lost.items()))

				embed.add_field(name="Units Killed", value="\n".join(units_lost_text))

			await ctx.send(embed=embed)

		else:
			await ctx.send(f"You failed your attack on **{target.display_name}**!")

		day_ago = dt.datetime.utcnow() - dt.timedelta(hours=24.0)

		await ctx.bot.db["empires"].update_one({"_id": ctx.author.id}, {"$set": {"last_attack": day_ago}}, upsert=True)


def setup(bot):
	bot.add_cog(Battles())
