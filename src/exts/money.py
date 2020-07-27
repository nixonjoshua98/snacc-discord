import random
import discord

from discord.ext import commands

from src import inputs
from src.common.models import BankM
from src.common.emoji import Emoji
from src.common.converters import DiscordUser


class Money(commands.Cog, name="Bank"):

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="free")
	async def free_money(self, ctx):
		""" Gain some free money """

		money = random.randint(500, 750)

		await ctx.bot.pool.execute(BankM.ADD_MONEY, ctx.author.id, money)

		await ctx.send(f"You gained **${money:,}**!")

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		""" Show your bank balance(s). """

		row = await BankM.get_row(ctx.bot.pool, ctx.author.id)

		embed = discord.Embed(title=f"{ctx.author.display_name}'s Bank", colour=discord.Color.orange())

		embed.description = f"{Emoji.BTC} **{row['BTC']}**\n:moneybag: **${row['money']:,}**"

		await ctx.send(embed=embed)

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="steal", cooldown_after_parsing=True)
	async def steal_coins(self, ctx, *, target: DiscordUser()):
		""" Attempt to steal from another user. """

		async with ctx.bot.pool.acquire() as con:
			target_bank = await BankM.get_row(con, target.id)

			target_money = target_bank["money"]

			stolen_amount = random.randint(max(1, int(target_money * 0.025)), max(1, int(target_money * 0.075)))

			thief_tax = int(stolen_amount // random.uniform(2.0, 8.0)) if stolen_amount >= 2_500 else 0

			await con.execute(BankM.ADD_MONEY, ctx.author.id, stolen_amount - thief_tax)
			await con.execute(BankM.SUB_MONEY, target.id, stolen_amount)

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
	bot.add_cog(Money())
