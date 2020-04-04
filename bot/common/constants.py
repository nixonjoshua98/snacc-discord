import enum


class DatabaseEnum(enum.IntEnum):
    LOCAL = 0,
    HEROKU = 1,
    LOCAL2HEROKU = 2,


class Bot:
    debug = True
    database = DatabaseEnum.LOCAL


CHANNEL_TAGS = ("abo", "game")
ROLE_TAGS = ("member", "default")
