import random

from discord.ext import commands

from src.common.models import BankM
from src.common.converters import NormalUser

from .moneyleaderboard import MoneyLeaderboard


class Money(commands.Cog):

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="free")
	async def free_money(self, ctx):
		""" Gain some free money """

		money = random.randint(500, 750)

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money)

		await ctx.send(f"You gained **${money:,}**!")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance. """

		row = await BankM.get_row(ctx.bot.pool, ctx.author.id)

		await ctx.send(f":moneybag: **{ctx.author.display_name}** has **${row['money']:,}**")

	@commands.cooldown(1, 60 * 75, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal_coins(self, ctx, target: NormalUser()):
		""" Attempt to steal from another user. """

		async with ctx.bot.pool.acquire() as con:
			author_bank = await BankM.get_row(con, ctx.author.id)
			target_bank = await BankM.get_row(con, target.id)

			author_money = author_bank["money"]
			target_money = target_bank["money"]

			stolen_amount = min(10_000, random.randint(1, int(target_money * 0.05)))

			await con.execute(BankM.ADD_MONEY, ctx.author.id, stolen_amount)
			await con.execute(BankM.SUB_MONEY, target.id, stolen_amount)

		await ctx.send(f"You stole **${stolen_amount:,}** from **{target.display_name}**")

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		await MoneyLeaderboard().send(ctx)
