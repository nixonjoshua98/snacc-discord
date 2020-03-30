import os

from snacc_bot.common.database import DBConnection


def path(file_name: str) -> str:
    return os.path.join(os.getcwd(), "snacc_bot", "resources", file_name)