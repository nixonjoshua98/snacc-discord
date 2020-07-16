import random

from discord.ext import commands

from src.common.models import BankM
from src.common.converters import NormalUser

from .moneyleaderboard import MoneyLeaderboard


class Money(commands.Cog):

	@commands.cooldown(1, 60 * 60 * 1, commands.BucketType.user)
	@commands.command(name="free")
	async def free_money(self, ctx):
		""" Gain some free money """

		money = random.randint(500, 1_000)

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money)

		await ctx.send(f"You gained **${money:,}**!")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx, user: NormalUser() = None):
		""" Show the bank balance of the user, or supply an optional target user. """

		user = user if user is not None else ctx.author

		row = await BankM.get_row(ctx.bot.pool, user.id)

		await ctx.send(f":moneybag: **{user.display_name}** has **${row['money']:,}**")

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		await MoneyLeaderboard().send(ctx)
