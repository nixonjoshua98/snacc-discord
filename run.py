from bot.structures.bot import SnaccBot

from bot.common.constants import DEBUGGING

# heroku pg:pull DATABASE_URL snaccbotdb -a snacc-bot

if __name__ == "__main__":
    print(f"Mode: {'DEBUG' if DEBUGGING else 'PRODUCTION'}")

    bot = SnaccBot()

    bot.load_extension("bot.cogs.wiki")

    bot.load_extension("bot.cogs.errorhandler")
    bot.load_extension("bot.cogs.listeners")
    bot.load_extension("bot.cogs.abo")
    bot.load_extension("bot.cogs.gambling")
    bot.load_extension("bot.cogs.money")
    bot.load_extension("bot.cogs.hangman")
    bot.load_extension("bot.cogs.stats")
    bot.load_extension("bot.cogs.settings")

    bot.run()
