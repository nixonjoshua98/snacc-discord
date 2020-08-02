
from discord.ext import commands

from src import inputs
from src.common import checks
from src.common.models import BankM, PopulationM, UserUpgradesM
from src.common.converters import EmpireUnit, Range

from src.exts.empire.units import MilitaryGroup, MoneyGroup


class Units(commands.Cog, name="Empire Units"):

	@checks.has_empire()
	@commands.command(name="units")
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		# - Load the data from the database
		author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)
		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)

		# - Unit pages
		money_units_page = MoneyGroup.create_units_page(author_population, author_upgrades).get()
		military_units_page = MilitaryGroup.create_units_page(author_population, author_upgrades).get()

		await inputs.send_pages(ctx, [money_units_page, military_units_page])

	@checks.has_empire()
	@commands.command(name="hire")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit to serve your empire. """

		# - Load the data
		author_upgrades = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)
		author_population = await PopulationM.fetchrow(ctx.bot.pool, ctx.author.id)
		author_bank = await BankM.fetchrow(ctx.bot.pool, ctx.author.id)

		# - Cost of upgrading from current -> (current + amount)
		price = unit.get_price(author_population[unit.db_col], amount)

		max_units = unit.get_max_amount(author_upgrades)

		# - Buying the unit will surpass the owned limit of that particular unit
		if author_population[unit.db_col] + amount > max_units:
			await ctx.send(f"**{unit.display_name}** have a limit of **{max_units}** units.")

		# - Author cannot afford to buy the unit
		elif price > author_bank["money"]:
			await ctx.send(f"You can't afford to hire **{amount}x {unit.display_name}**")

		else:
			# - Deduct the money from the authors bank
			await BankM.decrement(ctx.bot.pool, ctx.author.id, field="money", amount=price)

			# - Add the unit to the author's empire
			await PopulationM.increment(ctx.bot.pool, ctx.author.id, field=unit.db_col, amount=amount)

			await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")


def setup(bot):
	bot.add_cog(Units())
