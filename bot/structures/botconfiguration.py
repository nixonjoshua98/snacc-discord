import os

from configparser import ConfigParser


class BotConfiguration:
    def __init__(self):
        self.database = self._get_database_config()

    @staticmethod
    def _get_database_config():
        config = ConfigParser()

        config.read("postgres.ini")

        if os.getenv("DEBUG", False):
            return dict(config.items("postgres-local"))

        else:
            return {"DATABASE_URL": os.getenv("DATABASE_URL", None), "ssl": True}
