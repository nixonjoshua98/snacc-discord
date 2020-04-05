from bot.bot import SnaccBot

if __name__ == '__main__':
    dark = SnaccBot()

    dark.load_extension("bot.cogs.listeners")
    dark.load_extension("bot.cogs.abo")
    dark.load_extension("bot.cogs.serverconfig")
    dark.load_extension("bot.cogs.casino")
    dark.load_extension("bot.cogs.bank")

    dark.run("NjY2NjE2NTE1NDM2NDc4NDcz.XofF-Q.YNe2fpEgieFmOSrgBQVywdl4rRo")