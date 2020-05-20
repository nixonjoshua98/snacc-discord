
def run():
    import asyncio
    from bot.structures.bot import SnaccBot

    loop = asyncio.get_event_loop()

    bot = SnaccBot()

    #bot.load_extension("bot.cogs.wiki")

    bot.load_extension("bot.cogs.errorhandler")
    #bot.load_extension("bot.cogs.listeners")
    #bot.load_extension("bot.cogs.abo")
    bot.load_extension("bot.cogs.gambling")
    bot.load_extension("bot.cogs.money")
    #bot.load_extension("bot.cogs.hangman")
    bot.load_extension("bot.cogs.stats")
    #bot.load_extension("bot.cogs.settings")

    loop.create_task(bot.run())
