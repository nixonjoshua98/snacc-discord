
# heroku pg:pull DATABASE_URL snaccbot -a snacc-bot

if __name__ == "__main__":
    import bot
    import snacc
    import asyncio

    snacc.run()
    #bot.run()

    asyncio.get_event_loop().run_forever()
