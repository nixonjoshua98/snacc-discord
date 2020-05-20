from bot.common.queries import BankSQL


async def get_users_bals(pool, **users):
    return await _get_users_bals(pool, users)


async def get_author_bal(ctx):
    return (await _get_users_bals(ctx.bot.pool, {"author": ctx.author})).get("author", None)


async def get_user_bal(pool, user):
    return (await _get_users_bals(pool, {"user": user})).get("user", None)


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
