from bot.my_bot import MyBot

from bot.common.database import DBConnection

from bot.common import constants

import json

from bot.common import ServerConfigSQL, AboSQL, CoinsSQL

if __name__ == '__main__':
    dark = MyBot()

    """    
    if constants.Bot.database == constants.DatabaseEnum.LOCAL:
        with DBConnection(db_type=constants.DatabaseEnum.LOCAL2HEROKU) as con:
            con.cur.execute(ServerConfigSQL.SELECT_ALL)
            server_config = con.cur.fetchall()

            con.cur.execute(AboSQL.SELECT_ALL)
            abo = con.cur.fetchall()

            con.cur.execute(CoinsSQL.SELECT_ALL)
            coins = con.cur.fetchall()

            with DBConnection() as con2:
                for r in server_config:
                    params = [r.serverid, r.prefix, json.dumps(r.channels), json.dumps(r.roles)]
                    con.cur.execute(ServerConfigSQL.UPDATE, params)

                for r in abo:
                    params = [r.userid, r.lvl, r.trophies, r.dateset]
                    con.cur.execute(AboSQL.UPDATE, params)

                for r in coins:
                    params = [r.userid, r.balance]
                    con.cur.execute(CoinsSQL.UPDATE, params)
                    """

    dark.load_extension("bot.cogs.listeners")
    dark.load_extension("bot.cogs.vlisteners")

    dark.load_extension("bot.cogs.abo")
    dark.load_extension("bot.cogs.config")
    dark.load_extension("bot.cogs.casino")
    dark.load_extension("bot.cogs.bank")

    dark.run("NjY2NjE2NTE1NDM2NDc4NDcz.XofF-Q.YNe2fpEgieFmOSrgBQVywdl4rRo")

