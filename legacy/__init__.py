
def run():
    import asyncio
    from bot.structures.bot import SnaccBot

    loop = asyncio.get_event_loop()

    bot = SnaccBot()

    #legacy.load_extension("legacy.cogs.wiki")

    bot.load_extension("legacy.cogs.errorhandler")
    #legacy.load_extension("legacy.cogs.listeners")
    #legacy.load_extension("legacy.cogs.abo")
    bot.load_extension("legacy.cogs.gambling")
    bot.load_extension("legacy.cogs.money")
    #legacy.load_extension("legacy.cogs.hangman")
    bot.load_extension("legacy.cogs.stats")
    #legacy.load_extension("legacy.cogs.settings")

    loop.create_task(bot.run())
