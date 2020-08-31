
from discord.ext import commands

from src import inputs
from src.common import checks, EmpireConstants

from src.common.converters import EmpireUnit, Range, MergeableUnit

from src.data import Military, Workers

from src.structs.confirm import Confirm


class Units(commands.Cog):

	@checks.has_empire()
	@commands.group(name="units", aliases=["u"], invoke_without_command=True)
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		levels = await ctx.bot.mongo.find_one("levels", {"_id": ctx.author.id})

		pages = []

		for group in (Workers, Military):
			if len((page := group.shop_page(units, levels)).rows) > 0:
				pages.append(page.get())

		if pages:
			return await inputs.send_pages(ctx, pages)

		return await ctx.send("No units available to hire.")

	@checks.has_empire()
	@show_units.command(name="hire", aliases=["buy"])
	@commands.max_concurrency(1, commands.BucketType.user)
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, 100) = 1):
		""" Hire a new unit to serve your empire. """

		# - Load the data
		bank = await ctx.bot.mongo.find_one("bank", {"_id": ctx.author.id})
		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		levels = await ctx.bot.mongo.find_one("levels", {"_id": ctx.author.id})

		# - Cost of upgrading from current -> (current + amount)
		price = unit.calc_price(units.get(unit.key, 0), amount)

		# - Max owned number of the unit
		max_units = unit.calc_max_amount(levels.get(unit.key, 0))

		# - Buying the unit will surpass the owned limit of that particular unit
		if units.get(unit.key, 0) + amount > max_units:
			await ctx.send(f"**{unit.display_name}** have a limit of **{max_units}** units.")

		# - Author cannot afford to buy the unit
		elif price > bank.get("usd", 0):
			missing = price - bank.get('usd', 0)

			await ctx.send(f"You need an extra **${missing:,}** to hire **{amount}x {unit.display_name}**")

		else:
			# - Deduct the money from the authors bank
			await ctx.bot.mongo.decrement_one("bank", {"_id": ctx.author.id}, {"usd": price})

			await ctx.bot.mongo.increment_one("units", {"_id": ctx.author.id}, {unit.key: amount})

			await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")

	@checks.has_empire()
	@show_units.command(name="merge")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def merge_unit(self, ctx, unit: MergeableUnit()):
		""" Merge your units to upgrade their level. """

		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})
		levels = await ctx.bot.mongo.find_one("levels", {"_id": ctx.author.id})

		async def confirm():
			resp = True

			if ctx.bot.has_permissions(ctx.channel, add_reactions=True):
				resp = await Confirm(embed).prompt(ctx)

			return resp

		num_units = units.get(unit.key, 0)
		unit_level = levels.get(unit.key, 0)

		embed = ctx.bot.embed(
			title="Unit Merge",
			description=f"Level up **{unit.display_name}** by consuming **{EmpireConstants.MERGE_COST}** units?"
		)

		vale = [f"{k}: **{v}**" for k, v in unit.calc_next_merge_stats(num_units, unit_level).items()]

		embed.add_field(name="WARNING", value="\n".join(vale))

		if not await confirm():
			return await ctx.send("Merge cancelled.")

		await ctx.bot.mongo.increment_one("levels", {"_id": ctx.author.id}, {unit.key: 1})
		await ctx.bot.mongo.decrement_one("units", {"_id": ctx.author.id}, {unit.key: EmpireConstants.MERGE_COST})

		await ctx.send(f"**{unit.display_name}** has levelled up!")


def setup(bot):
	bot.add_cog(Units())
