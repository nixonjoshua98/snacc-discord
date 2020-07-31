
from discord.ext import commands

from src import inputs
from src.common import checks
from src.common.models import BankM, UserUpgradesM
from src.common.converters import EmpireUpgrade

from src.exts.shop.upgrades import ALL_UPGRADES

from src.structs.textpage import TextPage


class Shop(commands.Cog):

	async def cog_before_invoke(self, ctx):
		ctx.upgrades_["author"] = await UserUpgradesM.fetchrow(ctx.bot.pool, ctx.author.id)
		ctx.bank_["author"] = await BankM.fetchrow(ctx.bot.pool, ctx.author.id)

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

		page = self.create_upgrades_shop_page(ctx.upgrades_["author"])

		await inputs.send_pages(ctx, [page.get()])

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@shop_group.command(name="buy")
	async def buy_upgrade(self, ctx, upgrade: EmpireUpgrade()):
		""" Buy a new upgrade. """

		price = upgrade.get_price(ctx.upgrades_["author"][upgrade.db_col])

		max_units = upgrade.max_amount + ctx.upgrades_["author"]["extra_units"]

		if ctx.ctx.upgrades_["author"][upgrade.db_col] > max_units:
			await ctx.send(f"**{upgrade.display_name}** have an owned limit of **{max_units}**.")

		elif price > ctx.bank_["author"]["money"]:
			await ctx.send(f"You can't afford to hire **1x {upgrade.display_name}**")

		else:
			await BankM.decrement(ctx.bot.pool, ctx.author.id, field="money", amount=price)

			await UserUpgradesM.increment(ctx.bot.pool, ctx.author.id, field=upgrade.db_col, amount=1)

			await ctx.send(f"Bought **{upgrade.display_name}** for **${price:,}**!")

