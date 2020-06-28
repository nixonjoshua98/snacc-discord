import discord

from discord.ext import commands

from snacc.common.queries import BankSQL

from snacc.common.converters import NormalUser

from snacc.structs.leaderboards import RichestLeaderboard


class Money(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):

	@staticmethod
	async def get_balance(pool, user: discord.Member):
		async with pool.acquire() as con:
			async with con.transaction():
				row = await con.fetchrow(BankSQL.SELECT_USER, user.id)

				if row is None:
					await con.execute(BankSQL.INSERT_USER, user.id, 500)

					row = await con.fetchrow(BankSQL.SELECT_USER, user.id)

		return row

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx, user: NormalUser() = None):
		""" Show the bank balance of the user, or supply an optional target user. """

		user = user if user is not None else ctx.author

		bal = await self.get_balance(ctx.bot.pool, user)

		await ctx.send(f":moneybag: **{user.display_name}** has **${bal['money']:,}**.")

	@commands.cooldown(1, 60, commands.BucketType.guild)
	@commands.command(name="richest")
	async def show_richest_leaderboard(self, ctx):
		""" Display the richest players. """

		await RichestLeaderboard().send(ctx)


def setup(bot):
	bot.add_cog(Money())
