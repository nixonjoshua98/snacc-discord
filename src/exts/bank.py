import random

from discord.ext import commands

from src import inputs
from src.common.models import BankM
from src.common.converters import DiscordUser


class Bank(commands.Cog):

	@commands.command(name="free")
	async def free_money(self, ctx):
		await ctx.send(f"This command has been replaced with `{ctx.prefix}daily`")

	@commands.cooldown(1, 3_600 * 24, commands.BucketType.user)
	@commands.command(name="daily")
	async def daily(self, ctx):
		""" Gain your daily rewards. """

		hourly_income = max(250, await ctx.bot.get_cog("Empire").get_hourly_income(ctx.pool, ctx.author))

		money = random.randint(hourly_income // 2, hourly_income)

		await BankM.increment(ctx.pool, ctx.author.id, field="money", amount=money)

		await ctx.send(f"You have received **${money:,}**")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance(s). """

		author_bank = await BankM.fetchrow(ctx.bot.pool, ctx.author.id)

		msg = f"You have **${author_bank['money']:,}** and **{author_bank['btc']:,}** BTC"

		await ctx.send(msg)

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal_coins(self, ctx, *, target: DiscordUser()):
		""" Attempt to steal from another user. """

		author_bank = await BankM.fetchrow(ctx.bot.pool, ctx.author.id)
		target_bank = await BankM.fetchrow(ctx.bot.pool, target.id)

		min_stolen = int(target_bank["money"] * 0.025)
		max_stolen = min(author_bank["money"], int(target_bank["money"] * 0.075))

		stolen_amount = random.randint(max(1, min_stolen), max(1, max_stolen))

		thief_tax = int(stolen_amount // random.uniform(2.0, 8.0)) if stolen_amount >= 2_500 else 0

		await BankM.increment(ctx.bot.pool, ctx.author.id, field="money", amount=stolen_amount-thief_tax)
		await BankM.decrement(ctx.bot.pool, target.id, field="money", amount=stolen_amount)

		s = f"You stole **${stolen_amount:,}** from **{target.display_name}**."

		if thief_tax > 0:
			s = s[0:-1] + f" but the thief you hired took a cut of **${thief_tax:,}**."

		await ctx.send(s)

	@commands.cooldown(1, 15, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		async def query():
			return await ctx.bot.pool.fetch(BankM.SELECT_RICHEST)

		await inputs.show_leaderboard(ctx, "Richest Players", columns=["money"], order_by="money", query_func=query)


def setup(bot):
	bot.add_cog(Bank())
