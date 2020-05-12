import discord

from bot.common.queries import BankSQL
from bot.common.converters import DiscordUser


async def get_users_bals(pool, **users):
    return await _get_users_bals(pool, users)


async def get_author_bal(ctx):
    return (await _get_users_bals(ctx.bot.pool, {"author": ctx.author})).get("author", None)


async def get_ctx_users_bals(ctx):
    """
    Get all balances for each user in the command arguments and return them as a dict

    :param ctx: The context which we will look through the arguments for users
    :return: Return a dict of the user parameters with their balances
    """

    balances = {"author": ctx.author}

    for i, (name, param) in enumerate(ctx.command.clean_params.items(), start=2):
        value = ctx.args[i]

        if value is None:
            continue

        if isinstance(param.annotation, (DiscordUser, discord.Member, discord.User)):
            balances[name] = value

    return await _get_users_bals(ctx.bot.pool, balances)


async def _get_users_bals(pool, users: dict):
    balances = {}

    async with pool.acquire() as con:
        async with con.transaction():
            for key, user in users.items():
                row = await con.fetchrow(BankSQL.SELECT_USER, user.id)

                if row is None:
                    await con.execute(BankSQL.INSERT_USER, user.id, *BankSQL.DEFAULT_ROW.values())

                    row = await con.fetchrow(BankSQL.SELECT_USER, user.id)

                balances[key] = row

    return balances
