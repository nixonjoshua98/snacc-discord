
def run():
    import asyncio
    from snacc.classes.bot import SnaccBot

    loop = asyncio.get_event_loop()

    bot = SnaccBot()

    loop.create_task(bot.start())
