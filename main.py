import asyncio

from snacc_bot.snacc import SnaccBot
from snacc_bot.common.database import DBConnection
from src.my_bot import MyBot

if __name__ == '__main__':
    snacc = SnaccBot()
    dark = MyBot()

    with DBConnection() as con:
        con.cur.execute(con.get_query("create-table-coins.sql"))

    snacc.load_extension("snacc_bot.cogs.coins")
    snacc.load_extension("snacc_bot.cogs.casino")
    snacc.load_extension("snacc_bot.cogs.listeners")
    snacc.load_extension("snacc_bot.cogs.vlisteners")

    loop = asyncio.get_event_loop()

    loop.create_task(snacc.start("Njg5OTkxMDI3NjIwMzE1MjE4.XnK6SQ.GBti5-itZV4nJ461mgQVgy7DN8g"))

    loop.create_task(dark.start("NjY2NjE2NTE1NDM2NDc4NDcz.Xh2xCA.X8d9IFcSW_2e4c_maBMoXlxmI7Y"))

    loop.run_forever()

