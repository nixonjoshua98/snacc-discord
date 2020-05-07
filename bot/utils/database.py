import ssl
import os
import asyncpg

from configparser import ConfigParser


async def create_pool():
    # Local
    config = ConfigParser()
    config.read("./bot/config/postgres.ini")
    config = config.items("postgres")

    # Heroku
    ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Local
    if os.getenv("DEBUG", False):
        pool = await asyncpg.create_pool(**dict(config), max_size=20)

    # Heroku
    else:
        pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], ssl=ctx, max_size=20)

    return pool
