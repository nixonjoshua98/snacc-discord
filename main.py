from bot.bot import SnaccBot

if __name__ == '__main__':
    bot = SnaccBot()

    bot.load_extension("bot.cogs.listeners")
    bot.load_extension("bot.cogs.abo")
    bot.load_extension("bot.cogs.serverconfig")
    bot.load_extension("bot.cogs.casino")
    bot.load_extension("bot.cogs.bank")
    bot.load_extension("bot.cogs.fishing")
    bot.load_extension("bot.cogs.minigames")

    bot.run("NjY2NjE2NTE1NDM2NDc4NDcz.XofF-Q.YNe2fpEgieFmOSrgBQVywdl4rRo")