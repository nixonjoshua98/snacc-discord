from bot.bot import SnaccBot

if __name__ == "__main__":
    bot = SnaccBot()

    bot.load_extension("bot.cogs.abo")
    bot.load_extension("bot.cogs.gambling")
    bot.load_extension("bot.cogs.money")
    bot.load_extension("bot.cogs.hangman")
    bot.load_extension("bot.cogs.misc")
    bot.load_extension("bot.cogs.stats")
    bot.load_extension("bot.cogs.settings")

    bot.load_extension("bot.cogs.errorhandler")
    bot.load_extension("bot.cogs.listeners")

    bot.run("NjY2NjE2NTE1NDM2NDc4NDcz.XofF-Q.YNe2fpEgieFmOSrgBQVywdl4rRo")
