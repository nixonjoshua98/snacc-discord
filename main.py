import asyncio

from src.my_bot import MyBot

from src.common.database import DBConnection

if __name__ == '__main__':
    dark = MyBot()

    loop = asyncio.get_event_loop()

    with DBConnection() as con:
        con.cur.execute(con.get_query("create-abo-table.sql"))
        con.cur.execute(con.get_query("create-server-config-table.sql"))

    dark.load_extension("src.cogs.listeners")
    dark.load_extension("src.cogs.vlisteners")
    dark.load_extension("src.cogs.testing")

    dark.load_extension("src.cogs.auto_battles_online")
    dark.load_extension("src.cogs.config")
    dark.load_extension("src.cogs.casino")
    dark.load_extension("src.cogs.bank")

    dark.run("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y")

    loop.run_forever()

