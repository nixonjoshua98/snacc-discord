import ssl
import os
import asyncpg

from configparser import ConfigParser


async def create_pool():
    if os.getenv("DEBUG", False):
        pool = await _create_pool_from_config("./legacy/config/postgres.ini", "postgres")

    else:
        pool = await _create_pool_from_url(os.environ["DATABASE_URL"])

    return pool


async def _create_pool_from_config(file: str, section: str):
    config = ConfigParser()
    config.read(file)

    return await asyncpg.create_pool(**dict(config.items(section)), max_size=15)


async def _create_pool_from_url(url: str):
    return await asyncpg.create_pool(url, ssl=_create_ctx(), max_size=15)


def _create_ctx():
    ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    return ctx