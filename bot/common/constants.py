import enum


class DatabaseEnum(enum.IntEnum):
    LOCAL = 0,
    HEROKU = 1,
    LOCAL2HEROKU = 2,


class Bot:
    database = DatabaseEnum.HEROKU


ALL_CHANNEL_TAGS = ("abo", "game")
ALL_ROLE_TAGS = ("member", "default")
