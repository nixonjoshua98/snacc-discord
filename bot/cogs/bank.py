import discord

from discord.ext import commands

from bot.common.queries import BankSQL


class Bank(commands.Cog):
    DEFAULT_ROW = [500, 0]

    def __init__(self, bot):
        self.bot = bot

    async def get_user_balance(self, author: discord.Member):
        """
        Return the users bank row, or create a new user entry in the database if they do not exist and return that.

        :param discord.Member author: The user whose data we want to pull
        :return: The record which is linked ot the author
        """

        async with self.bot.pool.acquire() as con:
            async with con.transaction():
                user = await con.fetchrow(BankSQL.SELECT_USER, author.id)

                if user is None:
                    await con.execute(BankSQL.INSERT_USER, author.id, *self.DEFAULT_ROW)

                    user = await con.fetchrow(BankSQL.SELECT_USER, author.id)

        return user

    async def update_coins(self, author, amount):
        q = BankSQL.ADD_MONEY if amount > 0 else BankSQL.SUB_MONEY

        await self.bot.pool.execute(q, author.id, abs(amount))


def setup(bot):
    bot.add_cog(Bank(bot))
