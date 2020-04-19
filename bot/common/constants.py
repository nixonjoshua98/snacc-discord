import os
import enum


class DatabaseEnum(enum.IntEnum):
    LOCAL = 0,
    HEROKU = 1,
    LOCAL2HEROKU = 2,


class BotConstants:
    DEBUG = os.getenv("DEBUG", False)
    DATABASE = DatabaseEnum.LOCAL if DEBUG else DatabaseEnum.HEROKU


DARKNESS_GUILD = 666613802657382435
MEMBER_ROLE = 666615010579054614