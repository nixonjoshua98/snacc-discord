import discord

from discord.ext import commands

from bot.common.queries import BankSQL

from bot.common.converters import DiscordUser


class Bank(commands.Cog):
    DEFAULT_ROW = {"money": 500}

    def __init__(self, bot):
        self.bot = bot

    async def get_users_balances_in_args(self, ctx):
        """
        Get all balances for each user in the command arguments and return them as a dict

        :param ctx: The context which we will look through the arguments for users
        :return: Return a dict of the user parameters with their balances
        """

        balances = {"author": ctx.author}

        for i, (name, param) in enumerate(ctx.command.clean_params.items()):
            value = ctx.args[i]

            if value is None:
                continue

            if isinstance(param.annotation, (DiscordUser, discord.Member, discord.User)):
                balances[name] = value

        return await self.get_multiple_users_balances(balances)

    async def get_user_balance(self, user: discord.Member):
        """
        Return the users bank row, or create a new user entry in the database if they do not exist and return that.

        :param discord.Member user: The user whose data we want to pull
        :return: The record which is linked ot the author
        """

        balances = await self.get_multiple_users_balances({"user": user})

        return balances["user"]

    async def get_multiple_users_balances(self, users: dict):
        """
        Return the users bank row, or create a new user entry in the database if they do not exist and return that.
        """

        balances = {}

        async with self.bot.pool.acquire() as con:
            async with con.transaction():
                for key, user in users.items():
                    row = await con.fetchrow(BankSQL.SELECT_USER, user.id)

                    if row is None:
                        await con.execute(BankSQL.INSERT_USER, user.id, *self.DEFAULT_ROW.values())

                        row = await con.fetchrow(BankSQL.SELECT_USER, user.id)

                    balances[key] = row

        return balances

    async def update_money(self, author, amount):
        q = BankSQL.ADD_MONEY if amount > 0 else BankSQL.SUB_MONEY

        await self.bot.pool.execute(q, author.id, abs(amount))


def setup(bot):
    bot.add_cog(Bank(bot))
