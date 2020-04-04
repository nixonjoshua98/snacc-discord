import os
import enum


class DatabaseEnum(enum.IntEnum):
    LOCAL = 0,
    HEROKU = 1,
    LOCAL2HEROKU = 2,


class BotConstants:
    DATABASE = DatabaseEnum.LOCAL
    DEBUG = os.getenv("DEBUG", False)


CHANNEL_TAGS = ("abo", "game")
ROLE_TAGS = ("member", "default")
