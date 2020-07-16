import random

from discord.ext import commands

from src.common.models import BankM

from .moneyleaderboard import MoneyLeaderboard


class Money(commands.Cog):

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="free")
	async def free_money(self, ctx):
		""" Gain some free money """

		money = random.randint(500, 1_000)

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money)

		await ctx.send(f"You gained **${money:,}**!")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance. """

		row = await BankM.get_row(ctx.bot.pool, ctx.author.id)

		await ctx.send(f":moneybag: **{ctx.author.display_name}** has **${row['money']:,}**")

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		await MoneyLeaderboard().send(ctx)
