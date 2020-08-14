

import asyncio
import random
import discord
import itertools

import datetime as dt

from discord.ext import tasks, commands

from src import inputs
from src.common import MainServer, checks
from src.common.models import BankM, EmpireM, PopulationM, UserUpgradesM
from src.common.converters import EmpireUnit, Range, EmpireTargetUser

from src.data import MilitaryGroup, MoneyGroup

from src.exts.empire import utils, events


MAX_HOURS_OFFLINE = 8


class Empire(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.currently_adding_income = False

		self.start_income_loop()

	def start_income_loop(self):
		""" Start the background loop assuming that Snaccman is the owner. """

		async def predicate():
			if await self.bot.is_snacc_owner():
				print("Starting loop: Income")

				await asyncio.sleep(60 * 15)

				self.income_loop.start()

		asyncio.create_task(predicate())

	async def cog_before_invoke(self, ctx):
		if ctx.guild.id == MainServer.ID:
			await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=MainServer.EMPIRE_ROLE))

	async def cog_after_invoke(self, ctx):
		await EmpireM.set(ctx.bot.pool, ctx.author.id, last_login=dt.datetime.utcnow())

	@staticmethod
	def get_win_chance(atk_power, def_power):
		return max(0.15, min(0.85, ((atk_power / max(1, def_power)) / 2.0)))

	async def calculate_units_lost(self, population, upgrades):
		units_lost = dict()
		units_lost_cost = 0

		hourly_income = max(0, utils.get_hourly_money_change(population, upgrades))

		available_units = list(itertools.filterfalse(lambda u: population[u.db_col] == 0, MilitaryGroup.units))

		available_units.sort(key=lambda u: u.calculate_price(upgrades, population[u.db_col]), reverse=False)

		for unit in available_units:
			for i in range(1, population[unit.db_col] + 1):
				price = unit.calculate_price(upgrades, population[unit.db_col] - i, i)

				if (price + units_lost_cost) < hourly_income:
					units_lost[unit] = i

				units_lost_cost = sum([u.get_price(population[unit.db_col] - n, n) for u, n in units_lost.items()])

		return units_lost

	@staticmethod
	async def calculate_money_lost(bank):
		min_stolen = int(bank["money"] * 0.025)
		max_stolen = int(bank["money"] * 0.05)

		return random.randint(max(1, min_stolen), max(1, max_stolen))

	@checks.no_empire()
	@commands.command(name="create")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def create_empire(self, ctx, empire_name: str):
		""" Establish an empire under your name. """

		_ = await EmpireM.fetchrow(ctx.pool, ctx.author.id)

		await EmpireM.set(ctx.bot.pool, ctx.guild.id, name=empire_name)

		await ctx.send(f"Your empire has been established! You can rename your empire using `{ctx.prefix}rename`")

		await self.show_empire(ctx)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="empire", aliases=["e"])
	async def show_empire(self, ctx):
		""" View your empire. """

		async with ctx.pool.acquire() as con:
			empire = await EmpireM.fetchrow(con, ctx.author.id)
			upgrades = await UserUpgradesM.fetchrow(con, ctx.author.id)
			population = await PopulationM.fetchrow(con, ctx.author.id)

			quest_timer = await ctx.bot.get_cog("Quest").get_quest_timer(con, ctx.author)

		# - Calculate the values used in the Embed message
		hourly_income = MoneyGroup.get_total_hourly_income(population, upgrades)
		hourly_upkeep = MilitaryGroup.get_total_hourly_upkeep(population, upgrades)

		# - Quest text for the embed
		quest_text = quest_timer if quest_timer is None or quest_timer.total_seconds() > 0 else 'Finished'

		# - Create the Embed message which will be sent back to Discord
		embed = ctx.bot.embed(title=f"{str(ctx.author)}: {empire['name']}", thumbnail=ctx.author.avatar_url)

		total_power = MilitaryGroup.get_total_power(population)

		embed.add_field(name="General", value=(
			f"**Power Rating:** `{total_power:,}`\n"
			f"**Quest:** `{quest_text}`"
		))

		embed.add_field(name="Finances", value=(
			f"**Income:** `${hourly_income:,}`\n"
			f"**Upkeep:** `${hourly_upkeep:,}`"
		))

		await ctx.send(embed=embed)

	@checks.has_empire()
	@commands.command(name="rename")
	async def rename_empire(self, ctx, *, new_name):
		""" Rename your established empire. """

		await EmpireM.set(ctx.bot.pool, ctx.author.id, name=new_name)

		await ctx.send(f"Your empire has been renamed to `{new_name}`")

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="collect")
	async def collect_income(self, ctx):
		""" Collect your hourly income. """

		if self.currently_adding_income:
			return await ctx.send("Currently calculating and adding passive income. Please try again")

		now = dt.datetime.utcnow()

		async with ctx.pool.acquire() as con:
			empire = await EmpireM.fetchrow(con, ctx.author.id)
			population = await PopulationM.fetchrow(con, empire["empire_id"])
			upgrades = await UserUpgradesM.fetchrow(con, empire["empire_id"])

			hours_since_income = min(MAX_HOURS_OFFLINE, (now - empire["last_income"]).total_seconds() / 3600)

			money_change = utils.get_hourly_money_change(population, upgrades, hours=hours_since_income)

			await BankM.increment(con, empire["empire_id"], field="money", amount=money_change)

			await EmpireM.set(con, empire["empire_id"], last_income=now)

		await ctx.send(f"You received **${money_change:,}**")

	@checks.has_empire()
	@commands.cooldown(1, 15, commands.BucketType.user)
	@commands.command(name="scout", cooldown_after_parsing=True)
	async def scout(self, ctx, *, target: EmpireTargetUser()):
		""" Pay to scout an empire to recieve valuable information. """

		async with ctx.pool.acquire() as con:
			author_population = await PopulationM.fetchrow(con, ctx.author.id)
			target_population = await PopulationM.fetchrow(con, target.id)

			author_bank = await BankM.fetchrow(con, ctx.author.id)

			author_power = MilitaryGroup.get_total_power(author_population)
			target_power = MilitaryGroup.get_total_power(target_population)

			if author_bank["money"] < 500:
				await ctx.send(f"Scouting an empire costs **$500**.")

			else:
				await BankM.decrement(con, ctx.author.id, field="money", amount=500)

				win_chance = self.get_win_chance(author_power, target_power)

				await ctx.send(
					f"You hired a scout for **$500**. "
					f"You have a **{int(win_chance * 100)}%** chance of winning against **{target.display_name}**."
				)

	@checks.has_empire()
	@commands.cooldown(1, 60 * 120, commands.BucketType.user)
	@commands.command(name="attack", cooldown_after_parsing=True)
	async def attack(self, ctx, *, target: EmpireTargetUser()):
		""" Attack a rival empire. """

		async with ctx.pool.acquire() as con:

			# - Load the populations of each empire
			target_population = await PopulationM.fetchrow(con, target.id)
			author_population = await PopulationM.fetchrow(con, ctx.author.id)

			# - Power ratings of each empire which is used to calculate the win chance for the author (attacker)
			author_power = MilitaryGroup.get_total_power(author_population)
			target_power = MilitaryGroup.get_total_power(target_population)

			win_chance = self.get_win_chance(author_power, target_power)

			# - Author won the attack
			if win_chance >= random.uniform(0.0, 1.0):
				target_population = await PopulationM.fetchrow(con, target.id)
				target_upgrades = await UserUpgradesM.fetchrow(con, target.id)
				target_bank = await BankM.fetchrow(con, target.id)
				target_empire = await EmpireM.fetchrow(con, target.id)

				money_stolen = await self.calculate_money_lost(target_bank)

				units_lost = await self.calculate_units_lost(target_population, target_upgrades)

				bonus_money = int(money_stolen * (1.0 - win_chance) if win_chance <= 0.5 else 0)

				# - Perform the money pillaging - Transfer money from one account to the other
				await BankM.increment(con, ctx.author.id, field="money", amount=money_stolen+bonus_money)
				await BankM.decrement(con, target.id, field="money", amount=money_stolen+bonus_money)

				if units_lost:
					await PopulationM.decrement_many(con, target.id, {k.db_col: v for k, v in units_lost.items()})

				# - Put the target empire into a 'cooldown' so they cannot get attacked for a period of time
				await EmpireM.set(con, target.id, last_attack=dt.datetime.utcnow())

				# - Create the message to return to Discord
				units_text = "\n".join(map(lambda kv: f"{kv[1]}x {kv[0].display_name}", units_lost.items()))
				val = f"${money_stolen:,} {f'**+ ${bonus_money:,} bonus**' if bonus_money > 0 else ''}"

				embed = ctx.bot.embed(title=f"Attack on {str(target)}: {target_empire['name']}")

				embed.description = f"**Money Pillaged:** {val}"

				if units_text:
					embed.add_field(name="Units Killed", value=units_text)

				await ctx.send(embed=embed)

			else:
				author_bank = await BankM.fetchrow(con, ctx.author.id)

				money_lost = await self.calculate_money_lost(author_bank)

				await BankM.decrement(con, ctx.author.id, field="money", amount=money_lost)

				await ctx.send(f"Your attack on **{target.display_name}** failed and you lost **${money_lost:,}**")

			# - Take the author out of their cooldown
			await EmpireM.set(con, ctx.author.id, last_attack=dt.datetime.utcnow() - dt.timedelta(hours=24.0))

	@checks.has_empire()
	@commands.cooldown(1, 60 * 90, commands.BucketType.user)
	@commands.command(name="empireevent", aliases=["ee"])
	async def empire_event(self, ctx):
		""" Trigger an empire event. """

		options = (events.loot_event, events.stolen_event, events.assassinated_event, events.recruit_unit)
		weights = (85, 10, 10, 25)

		chosen_events = random.choices(options, weights=weights, k=1)

		for event in chosen_events:
			await event(ctx)

	@checks.has_empire()
	@commands.command(name="units")
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		# - Load the data from the database
		async with ctx.bot.acquire() as con:
			upgrades = await UserUpgradesM.fetchrow(con, ctx.author.id)
			population = await PopulationM.fetchrow(con, ctx.author.id)

		# - Unit pages
		money_units_page = MoneyGroup.create_units_page(population, upgrades).get()
		military_units_page = MilitaryGroup.create_units_page(population, upgrades).get()

		await inputs.send_pages(ctx, [money_units_page, military_units_page])

	@checks.has_empire()
	@commands.command(name="hire", aliases=["buy"])
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit to serve your empire. """

		# - Load the data
		upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)
		population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)
		bank = await BankM.fetchrow(ctx.bot.pool, ctx.author.id)

		# - Cost of upgrading from current -> (current + amount)
		price = unit.calculate_price(upgrades, population[unit.db_col], amount)

		max_units = unit.get_max_amount(upgrades)

		# - Buying the unit will surpass the owned limit of that particular unit
		if population[unit.db_col] + amount > max_units:
			await ctx.send(f"**{unit.display_name}** have a limit of **{max_units}** units.")

		# - Author cannot afford to buy the unit
		elif price > bank["money"]:
			await ctx.send(f"You can't afford to hire **{amount}x {unit.display_name}**")

		else:
			# - Deduct the money from the authors bank
			await BankM.decrement(ctx.bot.pool, ctx.author.id, field="money", amount=price)

			# - Add the unit to the author's empire
			await PopulationM.increment(ctx.bot.pool, ctx.author.id, field=unit.db_col, amount=amount)

			await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")

	@commands.cooldown(1, 15, commands.BucketType.guild)
	@commands.command(name="power", aliases=["empires"])
	async def power_leaderboard(self, ctx):
		""" Display the most powerful empires. """

		async def query():
			empires = await PopulationM.fetchall(ctx.pool)

			for i, row in enumerate(empires):
				empires[i] = dict(**row, __power__=MilitaryGroup.get_total_power(row))

			empires.sort(key=lambda ele: ele["__power__"], reverse=True)

			return empires

		await inputs.show_leaderboard(
			ctx,
			"Most Powerful Empires",
			columns=["__power__"],
			order_by="__power__",
			query_func=query,
			headers=["Power"]
		)

	@tasks.loop(hours=1.0)
	async def income_loop(self):
		""" Background income & upkeep loop. """

		self.currently_adding_income = True

		async with self.bot.pool.acquire() as con:
			# - Fetch all existing empires in the database
			empires = await EmpireM.fetchall(con)

			for empire in empires:
				now = dt.datetime.utcnow()

				# - Set the last_income field which is used to calculate the income rate from the delta time
				await EmpireM.set(con, empire["empire_id"], last_income=now)

				hours_since_login = (now - empire["last_login"]).total_seconds() / 3600

				# - User must have logged in the past 8 hours in order to get passive income
				if hours_since_login >= MAX_HOURS_OFFLINE:
					continue

				population = await PopulationM.fetchrow(con, empire["empire_id"])
				upgrades = await UserUpgradesM.fetchrow(con, empire["empire_id"])

				# - Total number of hours we need to credit the empire's bank
				hours_since_income = (now - empire["last_income"]).total_seconds() / 3600

				# - How much the user has earned (or lost) since their last income
				money_change = utils.get_hourly_money_change(population, upgrades, hours=hours_since_income)

				# - Increment the bank. Note: It can also be a negative
				await BankM.increment(con, empire["empire_id"], field="money", amount=money_change)

		self.currently_adding_income = False


def setup(bot):
	bot.add_cog(Empire(bot))
