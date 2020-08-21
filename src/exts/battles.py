
import random
import itertools

import datetime as dt

from discord.ext import commands

from src.common import checks

from src.common.converters import EmpireTargetUser, DiscordUser

from src.data import Military, Workers


THIEF_UNIT = Military.get(key="thief")
SCOUT_UNIT = Military.get(key="scout")


class Battles(commands.Cog):

	@staticmethod
	def get_win_chance(atk_power, def_power):
		return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))

	@staticmethod
	async def calculate_units_lost(units, levels):
		units_lost = dict()
		units_lost_cost = 0

		hourly_income = max(0, Workers.get_total_hourly_income(units, levels))

		hourly_upkeep = max(0, Military.get_total_hourly_upkeep(units, levels))

		hourly_income = hourly_income - hourly_upkeep

		all_units = Military.units + Workers.units

		available_units = list(itertools.filterfalse(lambda u: units.get(u.key, 0) == 0, all_units))

		available_units.sort(key=lambda u: u.calc_price(units.get(u.key, 0), 1), reverse=False)

		for unit in available_units:
			owned = units.get(unit.key, 0)

			for i in range(1, owned + 1):
				price = unit.calc_price(owned - i, i)

				if (price + units_lost_cost) < hourly_income or (units_lost_cost == 0):
					units_lost[unit] = i

				units_lost_cost = sum([unit.calc_price(owned - n, n) for u, n in units_lost.items()])

		return units_lost

	@checks.has_unit(THIEF_UNIT, 1)
	@commands.cooldown(1, 3_600, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal_coins(self, ctx, *, target: DiscordUser()):
		""" Attempt to steal from another user. """

		def calculate_money_lost(bank):
			min_val, max_val = int(bank.get("usd", 0) * 0.025), int(bank.get("usd", 0) * 0.05)

			return random.randint(max(1, min_val), max(1, max_val))

		# - Get data
		target_bank = await ctx.bot.mongo.find_one("bank", {"_id": target.id})

		stolen_amount = calculate_money_lost(target_bank)

		thief_tax = int(stolen_amount // random.uniform(2.0, 6.0)) if stolen_amount >= 0 else 0

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

	@checks.has_empire()
	@checks.has_power(25)
	@checks.has_unit(SCOUT_UNIT, 1)
	@commands.cooldown(1, 15, commands.BucketType.user)
	@commands.command(name="scout", cooldown_after_parsing=True)
	async def scout(self, ctx, *, target: EmpireTargetUser()):
		""" Pay to scout an empire to recieve valuable information. """

		# - Load data from database
		author_units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		target_units = await ctx.bot.mongo.find_one("units", {"_id": target.id})

		author_power = Military.get_total_power(author_units)
		target_power = Military.get_total_power(target_units)

		await ctx.bot.mongo.decrement_one("units", {"_id": ctx.author.id}, {SCOUT_UNIT.key: 1})

		win_chance = self.get_win_chance(author_power, target_power)

		await ctx.send(
			f"Your scout reports that you have a **{int(win_chance * 100)}%** "
			f"chance of winning against **{str(target)}**."
		)

	@checks.has_empire()
	@checks.has_power(25)
	@commands.cooldown(1, 60 * 120, commands.BucketType.user)
	@commands.command(name="attack", cooldown_after_parsing=True)
	async def attack(self, ctx, *, target: EmpireTargetUser()):
		""" Attack a rival empire. """

		# - Load author data
		author_units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		author_bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})

		# - Load target data
		target_bank = await ctx.bot.mongo.find_one("bank", {"_id": target.id})
		target_units = await ctx.bot.mongo.find_one("units", {"_id": target.id})
		target_empire = await ctx.bot.mongo.find_one("empires", {"_id": target.id})
		target_levels = await ctx.bot.mongo.find_one("levels", {"_id": target.id})

		# - Power ratings of each empire which is used to calculate the win chance for the author (attacker)
		target_power = Military.get_total_power(target_units)
		author_power = Military.get_total_power(author_units)

		# - Author chance of winning against the target
		win_chance = self.get_win_chance(author_power, target_power)

		# - Author won the attack
		if win_chance >= random.uniform(0.0, 1.0):

			hourly_income = max(0, Workers.get_total_hourly_income(target_units, target_levels))

			hourly_upkeep = max(0, Military.get_total_hourly_upkeep(target_units, target_levels))

			hourly_income = max(0, hourly_income - hourly_upkeep)

			# - Calculate pillage amount
			extra = (target_bank.get("usd", 0) // 100_000) * 0.05

			min_val = max(0, int(target_bank.get("usd", 0) * (0.025 + extra)))
			max_val = max(0, int(target_bank.get("usd", 0) * (0.050 + extra)))

			money_stolen = min(hourly_income, random.randint(min_val, max_val))

			# - Add a bonus pillage amount if the chance of winning is less than 50%
			bonus_money = int((money_stolen * 2.0) * (1.0 - win_chance) if win_chance <= 0.50 else 0)

			# - Increment and decrement the balances of the two users
			await ctx.bot.mongo.increment_one("bank", {"_id": ctx.author.id}, {"usd": money_stolen + bonus_money})
			await ctx.bot.mongo.decrement_one("bank", {"_id": target.id}, {"usd": money_stolen + bonus_money})

			# - Units killed
			units_lost = await self.calculate_units_lost(target_units, target_levels)

			# - Deduct the units killed from the target
			if units_lost:
				units_lost_keys = {k.key: v for k, v in units_lost.items()}

				await ctx.bot.mongo.decrement_one("units", {"_id": target.id}, units_lost_keys)

			# - Put the target empire into a 'cooldown' so they cannot get attacked for a period of time
			await ctx.bot.mongo.update_one("empires", {"_id": target.id}, {"last_attack": dt.datetime.utcnow()})

			# - Create the message to return to Discord
			val = f"${money_stolen:,} {f'**+ ${bonus_money:,} bonus**' if bonus_money > 0 else ''}"

			embed = ctx.bot.embed(
				title=f"Attack on {str(target)}: {target_empire.get('name', target.display_name)}",
				description=f"**Money Pillaged:** {val}"
			)

			if units_lost:
				embed.add_field(
					name="Units Killed",
					value="\n".join(map(lambda kv: f"{kv[1]}x {kv[0].display_name}", units_lost.items()))
				)

			await ctx.send(embed=embed)

		else:
			# - Calculate pillage amount
			min_val = min(2_500, int(author_bank.get("usd", 0) * 0.025))
			max_val = min(10_000, int(author_bank.get("usd", 0) * 0.050))

			money_lost = random.randint(max(0, min_val), max(0, max_val))

			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": money_lost})

			await ctx.send(f"Your attack on **{target.display_name}** failed and you lost **${money_lost:,}**")

		# - Take the author out of their cooldown
		day_ago = dt.datetime.utcnow() - dt.timedelta(hours=24.0)

		await ctx.bot.mongo.update_one("empires", {"_id": ctx.author.id}, {"last_attack": day_ago})


def setup(bot):
	bot.add_cog(Battles())
