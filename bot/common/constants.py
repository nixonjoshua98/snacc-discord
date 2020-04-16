import os
import enum


class DatabaseEnum(enum.IntEnum):
    LOCAL = 0,
    HEROKU = 1,
    LOCAL2HEROKU = 2,


class BotConstants:
    DEBUG = os.getenv("DEBUG", False)
    DATABASE = DatabaseEnum.LOCAL if DEBUG else DatabaseEnum.HEROKU