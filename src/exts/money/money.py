import discord
import random

from discord.ext import commands

from src.common.queries import BankSQL

from src.common.converters import NormalUser

from .moneyleaderboard import MoneyLeaderboard


class Money(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):

	async def get_user_balance(self, con, user: discord.Member):
		bal = await con.fetchrow(BankSQL.SELECT_USER, user.id)

		if bal is None:
			bal = await con.fetchrow(BankSQL.INSERT_USER, user.id)

		return bal

	@commands.cooldown(1, 60 * 60 * 1, commands.BucketType.user)
	@commands.command(name="free")
	async def free_money(self, ctx):
		""" Gain some free money """

		money = random.randint(500, 1_500)

		await ctx.bot.pool.execute(BankSQL.ADD_MONEY, ctx.author.id, money)

		await ctx.send(f"You gained **${money:,}**!")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx, user: NormalUser() = None):
		""" Show the bank balance of the user, or supply an optional target user. """

		user = user if user is not None else ctx.author

		bal = self.get_user_balance(ctx.bot.pool, user)

		await ctx.send(f":moneybag: **{user.display_name}** has **${bal['money']:,}**")

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		await MoneyLeaderboard().send(ctx)
