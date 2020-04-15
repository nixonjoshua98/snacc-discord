import asyncio

from bot.bot import SnaccBot

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    bot = SnaccBot()

    bot.load_extension("bot.cogs.listeners")
    bot.load_extension("bot.cogs.abo")
    bot.load_extension("bot.cogs.serverconfig")
    bot.load_extension("bot.cogs.casino")
    bot.load_extension("bot.cogs.coins")

    loop.create_task(bot.start("NjY2NjE2NTE1NDM2NDc4NDcz.XofF-Q.YNe2fpEgieFmOSrgBQVywdl4rRo"))

    loop.run_forever()