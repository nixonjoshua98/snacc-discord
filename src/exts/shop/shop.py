
from discord.ext import commands

from src import inputs
from src.common import checks
from src.common.models import BankM, UserUpgradesM
from src.common.converters import ShopItem

from src.exts.shop.upgrades import ALL_UPGRADES

from src.structs.textpage import TextPage


class Shop(commands.Cog):
	@staticmethod
	def create_upgrades_shop_page(upgrades):
		page = TextPage(title="Empire Upgrades", headers=["ID", "Name", "Owned", "Cost"])

		for upgrade in ALL_UPGRADES:
			if upgrades[upgrade.db_col] < upgrade.max_amount:
				price = f"{upgrade.get_price(upgrades[upgrade.db_col]):,}"
				owned = f"{upgrades[upgrade.db_col]}/{upgrade.max_amount}"

				page.add_row([upgrade.id, upgrade.display_name, owned, price])

		page.set_footer("No upgrades available to buy" if len(page.rows) == 0 else None)

		return page

	@checks.has_empire()
	@commands.group(name="shop", invoke_without_command=True)
	async def shop_group(self, ctx):
		""" Display your shop. """

		upgrades = await UserUpgradesM.get_row(ctx.bot.pool, ctx.author.id)

		page = self.create_upgrades_shop_page(upgrades)

		await inputs.send_pages(ctx, [page.get()])

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@shop_group.command(name="buy")
	async def buy_item(self, ctx, item: ShopItem()):
		""" Buy a new upgrade. """

		async with ctx.bot.pool.acquire() as con:
			upgrades = await UserUpgradesM.get_row(con, ctx.author.id)

			bank = await BankM.get_row(con, ctx.author.id)

			price = item.get_price(upgrades[item.db_col])

			max_units = item.max_amount + upgrades["extra_units"]

			if upgrades[item.db_col] > max_units:
				await ctx.send(f"**{item.display_name}** have an owned limit of **{max_units}**.")

			elif price > bank["money"]:
				await ctx.send(f"You can't afford to hire **1x {item.display_name}**")

			else:
				await con.execute(BankM.SUB_MONEY, ctx.author.id, price)

				await UserUpgradesM.add_upgrade(con, ctx.author.id, item, 1)

				await ctx.send(f"Bought **{item.display_name}** for **${price:,}**!")

