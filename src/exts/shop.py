

from discord.ext import commands

from src.common import checks
from src.common.converters import EmpireUpgrade, Range

from src.structs.textpage import TextPage
from src.structs.displaypages import DisplayPages

from src.common.upgrades import EmpireUpgrades


class Shop(commands.Cog):

	@checks.has_empire()
	@commands.group(name="shop", invoke_without_command=True)
	async def shop_group(self, ctx):
		""" Display your shop. """

		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

		all_upgrades = empire.get("upgrades", dict()) if empire is not None else dict()

		pages = []

		for title, upgrades in EmpireUpgrades.groups.items():
			page = TextPage(title=title, headers=["ID", "Name", "Owned", "Cost"])

			for upgrade in upgrades:
				owned = all_upgrades.get(upgrade.key, 0)

				if owned < upgrade.max_amount:
					price = f"${upgrade.calc_price(owned, 1):,}"
					owned = f"{owned}/{upgrade.max_amount}"

					page.add([upgrade.id, upgrade.display_name, owned, price])

			page.set_footer("No upgrades available to buy" if len(page.rows) == 0 else None)

			pages.append(page.get())

		await DisplayPages(pages, timeout=180.0).send(ctx)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@shop_group.command(name="buy")
	async def buy_upgrade(self, ctx, upgrade: EmpireUpgrade(), amount: Range(1, None) = 1):
		""" Buy a new upgrade. """

		# - Query the database
		empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id}) or dict()

		bank = await ctx.bot.db["bank"].find_one({"_id": ctx.author.id}) or dict()

		all_upgrades = empire.get("upgrades", dict())

		owned = all_upgrades.get(upgrade.key, 0)
		price = upgrade.calc_price(owned, amount)

		# - Reached the owned limit
		if owned + amount > upgrade.max_amount:
			await ctx.send(f"**{upgrade.display_name}** have an owned limit of **{upgrade.max_amount}**")

		# - User cannot afford upgrade
		elif price > bank.get("usd", 0):
			await ctx.send(f"You can't afford to hire **{amount}x {upgrade.display_name}**")

		else:
			# - Update database
			await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": -price}}, upsert=True)

			await ctx.bot.db["empires"].update_one(
				{"_id": ctx.author.id},
				{"$inc": {f"upgrades.{upgrade.key}": amount}},
				upsert=True
			)

			await ctx.send(f"Bought **{amount}x {upgrade.display_name}** for **${price:,}**!")


def setup(bot):
	bot.add_cog(Shop())
