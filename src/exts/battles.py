
import random
import itertools

import datetime as dt

from src import utils

from discord.ext import commands

from src.common import checks

from src.common.converters import EmpireTargetUser, DiscordUser


from src.data import Military


THIEF_UNIT = Military.get(key="thief")
SCOUT_UNIT = Military.get(key="scout")


class Battles(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@checks.has_unit(THIEF_UNIT, 1)
	@commands.cooldown(1, 3_600, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal(self, ctx, *, target: DiscordUser()):
		""" Attempt to steal from another user. """

		def calculate_money_lost(bank):
			min_val, max_val = int(bank.get("usd", 0) * 0.015), int(bank.get("usd", 0) * 0.025)

			return random.randint(max(1, min_val), max(1, max_val))

		# - Get data
		target_bank = await ctx.bot.mongo.find_one("bank", {"_id": target.id})

		stolen_amount = calculate_money_lost(target_bank)

		thief_tax = int(stolen_amount // random.uniform(2.0, 6.0)) if stolen_amount >= 3_000 else 0

		# - Perform money transfers
		await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": stolen_amount - thief_tax})
		await ctx.bot.mongo.decrement_one("bank", {"_id": target.id}, {"usd": stolen_amount})

		s = f"You stole **${stolen_amount:,}** from **{target.display_name}!**"

		if thief_tax > 0:
			if random.random() <= 0.25:
				await ctx.bot.mongo.decrement_one("units", {"_id": ctx.author.id}, {THIEF_UNIT.key: 1})

				s = s[0:-3] + f" **but the thief you hired stole and escaped with **${thief_tax:,}**."

			else:
				s = s[0:-3] + f" **but the thief you hired took a cut of **${thief_tax:,}**."

		await ctx.send(s)

	@checks.has_unit(SCOUT_UNIT, 1)
	@commands.cooldown(1, 15, commands.BucketType.user)
	@commands.command(name="scout", cooldown_after_parsing=True)
	async def scout(self, ctx, *, target: EmpireTargetUser()):
		""" Send a scout to a rival empire to search for information """

		# - Load data from database
		author_units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		target_units = await ctx.bot.mongo.find_one("units", {"_id": target.id})

		author_power = Military.calc_total_power(author_units)
		target_power = Military.calc_total_power(target_units)

		win_chance = self.calc_win_chance(author_power, target_power)

		await ctx.send(
			f"Your scout reports that you have a **{int(win_chance * 100)}%** "
			f"chance of winning against **{str(target)}**."
		)

	@checks.has_power(25)
	@commands.cooldown(1, 60 * 120, commands.BucketType.user)
	@commands.command(name="attack", cooldown_after_parsing=True)
	async def attack(self, ctx, *, target: EmpireTargetUser()):
		""" Attack a rival empire. """

		# - Load data
		a_units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		t_units = await ctx.bot.mongo.find_one("units", {"_id": target.id})

		# - Power ratings of each empire which is used to calculate the win chance for the author (attacker)
		target_power = Military.calc_total_power(t_units)
		author_power = Military.calc_total_power(a_units)

		# - Author chance of winning against the target
		win_chance = self.calc_win_chance(author_power, target_power)

		# - Author won the attack
		if win_chance >= random.uniform(0.0, 1.0):
			# - Load the targets data
			t_bank, t_levels, t_empire = await ctx.bot.mongo.find_one_many(
				["bank", "levels", "empires"],
				{"_id": target.id}
			)

			# - Units killed
			units_lost = await self.calc_units_lost(t_units, t_levels)

			if units_lost:
				units_lost_keys = {k.key: v for k, v in units_lost.items()}

				# - Deduct the units killed from the target
				await ctx.bot.mongo.decrement_one("units", {"_id": target.id}, units_lost_keys)

			# - Calculate the stolen/pillaged amount
			stolen_amount, bonus_money = self.calc_pillaged_amount(
				t_units,
				t_levels,
				t_bank,
				win_chance,
				1.0 if units_lost else 2.0
			)

			# - Increment and decrement the balances of the two users
			await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": stolen_amount + bonus_money})
			await ctx.bot.mongo.decrement_one("bank", {"_id": target.id}, {"usd": stolen_amount + bonus_money})

			# - Put the target empire into a 'cooldown' so they cannot get attacked for a period of time
			await ctx.bot.mongo.set_one("empires", {"_id": target.id}, {"last_attack": dt.datetime.utcnow()})

			# - Create the message to return to Discord
			val = f"${stolen_amount:,} {f'**+ ${bonus_money:,} bonus**' if bonus_money > 0 else ''}"

			embed = ctx.bot.embed(
				title=f"Attack on {str(target)}: {t_empire.get('name', target.display_name)}",
				description=f"**Money Pillaged:** {val}"
			)

			# - Actually a list...
			units_lost_text = list(map(lambda kv: f"`{kv[1]}x {kv[0].display_name}`", units_lost.items()))

			if units_lost:
				embed.add_field(name="Units Killed", value="\n".join(units_lost_text))

			await ctx.send(embed=embed)

		else:
			await ctx.send(f"You failed your attack on **{target.display_name}**!")

		# - Take the author out of their cooldown
		day_ago = dt.datetime.utcnow() - dt.timedelta(hours=24.0)

		await ctx.bot.mongo.set_one("empires", {"_id": ctx.author.id}, {"last_attack": day_ago})

	@staticmethod
	def calc_win_chance(atk_power, def_power):
		return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))

	@staticmethod
	def calc_pillaged_amount(units, levels, bank, win_chance, multiplier: int = 1.0):
		hourly_income = max(0, utils.net_income(units, levels))

		min_val = max(0, int(bank.get("usd", 0) * 0.025))
		max_val = max(0, int(bank.get("usd", 0) * 0.050))

		stolen_amount = int(min(bank.get("usd", 0), hourly_income, random.randint(min_val, max_val) * multiplier))

		# - Add a bonus pillage amount if the chance of winning is less than 50%
		bonus_money = int((stolen_amount * 2.0) * (1.0 - win_chance) if win_chance < 0.50 else 0)

		return stolen_amount, bonus_money

	@staticmethod
	def calc_failed_attack_lose(units, levels, bank):
		hourly_income = max(0, utils.net_income(units, levels))

		min_val = min(2_500, int(bank.get("usd", 0) * 0.025))
		max_val = min(10_000, int(bank.get("usd", 0) * 0.050))

		return int(min(bank.get("usd", 0), hourly_income, random.randint(min_val, max_val)))

	@staticmethod
	async def calc_units_lost(units, levels):
		units_lost = dict()
		units_lost_cost = 0

		hourly_income = max(0, utils.net_income(units, levels))

		available_units = list(itertools.filterfalse(lambda u: units.get(u.key, 0) == 0, Military.units))

		available_units.sort(key=lambda u: u.calc_price(units.get(u.key, 0), 1), reverse=False)

		for unit in available_units:
			owned = units.get(unit.key, 0)

			for i in range(1, owned + 1):
				price = unit.calc_price(owned - i, i)

				if (price + units_lost_cost) < hourly_income:
					units_lost[unit] = i

				units_lost_cost = sum([unit.calc_price(owned - n, n) for u, n in units_lost.items()])

		return units_lost


def setup(bot):
	bot.add_cog(Battles(bot))
