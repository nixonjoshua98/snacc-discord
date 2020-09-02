
from discord.ext import commands

from src.common import EmpireConstants, checks
from src.common.converters import EmpireUnit, Range, MergeableUnit
from src.common.population import Workers, Military

from src.structs.confirm import Confirm
from src.structs.displaypages import DisplayPages


class Units(commands.Cog):

	@checks.has_empire()
	@commands.group(name="units", aliases=["u"], invoke_without_command=True)
	async def show_units(self, ctx):
		""" Show all the possible units which you can buy. """

		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		pages = []

		for group in (Workers, Military):
			page = group.shop_page(empire)

			pages.append(page.get())

		await DisplayPages(pages).send(ctx)

	@checks.has_empire()
	@show_units.command(name="hire", aliases=["buy"])
	async def hire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, None) = 1):
		""" Hire a new unit to serve your empire. """

		bank = await ctx.bot.db["bank"].find_one({"_id": ctx.author.id})
		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		# - Get the data for the entry the user wants to buy
		unit_entry = empire.get("units", dict()).get(unit.key, dict()) if empire is not None else dict()

		# - Bank
		bank = bank if bank is not None else dict()

		# - Calculate values about the unit
		price = unit.calc_price(unit_entry.get("owned", 0), amount)
		max_owned = unit.calc_max_amount(unit_entry)

		# - Buying the unit will surpass the owned limit of that particular unit
		if unit_entry.get("owned", 0) + amount > max_owned:
			await ctx.send(f"**{unit.display_name}** have a limit of **{max_owned}** units.")

		# - Author cannot afford to buy the unit
		elif price > bank.get("usd", 0):
			missing = price - bank.get('usd', 0)

			await ctx.send(f"You need an extra **${missing:,}** to hire **{amount}x {unit.display_name}**")

		else:
			await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": -price}}, upsert=True)

			await ctx.bot.db["empires"].update_one(
				{"_id": ctx.author.id},
				{"$inc": {f"units.{unit.key}.owned": amount}},
				upsert=True
			)

			await ctx.send(f"Bought **{amount}x {unit.display_name}** for **${price:,}**!")

	@checks.has_empire()
	@show_units.command(name="fire")
	async def fire_unit(self, ctx, unit: EmpireUnit(), amount: Range(1, None) = 1):
		""" Fire a unit. You get no money back from firing. """

		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		# - Get the data for the entry the user wants to buy
		unit_entry = empire.get("units", dict()).get(unit.key, dict()) if empire is not None else dict()

		if unit_entry.get("owned", 0) - amount < 0:
			await ctx.send(f"You do not have **{amount:,}x {unit.key}** available to fire.")

		else:
			await ctx.bot.db["empires"].update_one(
				{"_id": ctx.author.id},
				{"$inc": {f"units.{unit.key}.owned": -amount}},
				upsert=True
			)

			await ctx.send(f"Fired **{amount}x {unit.display_name}**!")

	@checks.has_empire()
	@show_units.command(name="merge")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def merge_unit(self, ctx, unit: MergeableUnit()):
		""" Merge your units to upgrade their level. """

		async def confirm():
			resp = True

			if ctx.bot.has_permissions(ctx.channel, add_reactions=True):
				resp = await Confirm(embed).prompt(ctx)

			return resp

		embed = ctx.bot.embed(title="Unit Merge", author=ctx.author)

		embed.add_field(
			name="WARNING",
			value=f"Level up **{unit.display_name}** by consuming **{EmpireConstants.MERGE_COST}** units?"
		)

		# - Double check that this is what the user wants to do
		if not await confirm():
			return await ctx.send("Merge cancelled.")

		await ctx.bot.db["empires"].update_one(
			{"_id": ctx.author.id},
			{
				"$inc": {
					f"units.{unit.key}.owned": -EmpireConstants.MERGE_COST,
					f"units.{unit.key}.level": 1
				}
			},
			upsert=True
		)

		await ctx.send(f"**{unit.display_name}** has levelled up!")


def setup(bot):
	bot.add_cog(Units())
