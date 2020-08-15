
from discord.ext import commands

from src import inputs
from src.common import checks
from src.common.converters import EmpireUnit, Range

from src.data import MilitaryGroup, MoneyGroup


class Units(commands.Cog):

	@checks.has_empire()
	@commands.command(name="units")
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		# - Load the data from the database
		workers = await ctx.bot.mongo.find_one("workers", {"_id": ctx.author.id})
		upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})
		military = await ctx.bot.mongo.find_one("military", {"_id": ctx.author.id})

		# - Unit pages
		money_units_page = MoneyGroup.create_units_page(workers, upgrades).get()

		military_units_page = MilitaryGroup.create_units_page(military, upgrades).get()

		await inputs.send_pages(ctx, [money_units_page, military_units_page])

	@checks.has_empire()
	@commands.command(name="hire", aliases=["buy"])
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit to serve your empire. """

		# - Load the data
		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})
		upgrades = await ctx.bot.mongo.find_one("upgrades", {"_id": ctx.author.id})

		units = await ctx.bot.mongo.find_one(unit.collection, {"_id": ctx.author.id})

		# - Cost of upgrading from current -> (current + amount)
		price = unit.price(upgrades, units.get(unit.key, 0), amount)

		max_units = unit.max_amount(upgrades)

		# - Buying the unit will surpass the owned limit of that particular unit
		if units.get(unit.key, 0) + amount > max_units:
			await ctx.send(f"**{unit.display_name}** have a limit of **{max_units}** units.")

		# - Author cannot afford to buy the unit
		elif price > bank.get("usd", 0):
			await ctx.send(f"You can't afford to hire **{amount}x {unit.display_name}**")

		else:
			# - Deduct the money from the authors bank
			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": price})

			await ctx.bot.mongo.increment_one(unit.collection, {"_id": ctx.author.id}, {unit.key: amount})

			await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")


def setup(bot):
	bot.add_cog(Units())
