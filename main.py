from bot.bot import SnaccBot

from bot.common import DBConnection

if __name__ == '__main__':
    bot = SnaccBot()

    with DBConnection() as con:
        con.cur.execute("DROP TABLE IF EXISTS fishing;")

    bot.load_extension("bot.cogs.listeners")
    bot.load_extension("bot.cogs.abo")
    bot.load_extension("bot.cogs.serverconfig")
    bot.load_extension("bot.cogs.casino")
    bot.load_extension("bot.cogs.coins")

    bot.run("NjY2NjE2NTE1NDM2NDc4NDcz.XofF-Q.YNe2fpEgieFmOSrgBQVywdl4rRo")