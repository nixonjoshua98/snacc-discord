import enum


class DatabaseEnum(enum.IntEnum):
    LOCAL = 0,
    HEROKU = 1,
    LOCAL2HEROKU = 2,


class Bot:
    debug = False
    database = DatabaseEnum.HEROKU


CHANNEL_TAGS = ("abo", "game")
ROLE_TAGS = ("member", "default")
