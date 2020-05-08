from bot.common.queries import ServersSQL

DEFAULT_ROW = {"prefix": "!", "entryRole": 0, "memberRole": 0}


async def get_server_settings(pool, guild):
    """ Return the server configuration or add a new entry and return the default configuration """

    async with pool.acquire() as con:
        async with con.transaction():
            svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

            if svr is None:
                await con.execute(ServersSQL.INSERT_SERVER, guild.id, *DEFAULT_ROW.values())

                svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

    return svr
