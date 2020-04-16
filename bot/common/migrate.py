from bot.common.queries import ServersSQL, BankSQL

from bot.common import (DBConnection,)

from bot.common import DatabaseEnum


async def run(bot):
    with DBConnection(DatabaseEnum.LOCAL2HEROKU) as con:
        con.cur.execute("SELECT * FROM coins;")

        results = con.cur.fetchall()

        bank = bot.get_cog("Bank")
        settings = bot.get_cog("Settings")

        for r in results:
            id_ = r.userid

            bal = max(bank.DEFAULT_ROW[0], r.balance)

            await bot.pool.execute(BankSQL.INSERT_USER, id_, *bank.DEFAULT_ROW)
            await bot.pool.execute(BankSQL.SET_COINS, id_, bal)

        con.cur.execute("SELECT * FROM server_config;")

        results = con.cur.fetchall()

        for r in results:
            id_ = r.serverid

            await bot.pool.execute(ServersSQL.INSERT_SERVER, id_, *settings.DEFAULT_ROW)

            prefix = getattr(r, "prefix", bot.default_prefix) or bot.default_prefix

            roles = getattr(r, "roles", None)

            entry = roles.get("default", 0)

            await bot.pool.execute(ServersSQL.UPDATE_PREFIX, id_, prefix)
            await bot.pool.execute(ServersSQL.UPDATE_ENTRY_ROLE, id_, entry)
