
from snacc.common.queries import ServersSQL


async def get_server_settings(pool, guild):
    """ Return the server configuration or add a new entry and return the default configuration """

    async with pool.acquire() as con:
        async with con.transaction():
            svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

            if svr is None:
                await con.execute(ServersSQL.INSERT_SERVER, guild.id, *ServersSQL.DEFAULT_ROW.values())

                svr = await con.fetchrow(ServersSQL.SELECT_SERVER, guild.id)

    return svr
