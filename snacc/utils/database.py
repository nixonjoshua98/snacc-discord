import os
import ssl
import asyncpg

from snacc import utils


async def create_pool():
    print("Creating connection pool...", end="")

    if os.getenv("DEBUG", False):
        pool = await _create_pool_from_config("./snacc/config/postgres.ini", "postgres")

    else:
        pool = await _create_pool_from_url(os.environ["DATABASE_URL"])

    print("OK")

    return pool


async def _create_pool_from_config(file: str, section: str):
    config = utils.load_config(file, section)

    return await asyncpg.create_pool(**config, max_size=15)


async def _create_pool_from_url(url: str):
    ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return await asyncpg.create_pool(url, ssl=ctx, max_size=15)