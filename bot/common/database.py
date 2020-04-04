import os
import psycopg2
import psycopg2.extras

from configparser import ConfigParser

from bot.common import utils

from bot.common import constants


class DBConnection:
    def __init__(self, db_type=None):
        database_type = constants.Bot.database if db_type is None else db_type

        if database_type == constants.DatabaseEnum.HEROKU:
            self._con = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

        else:
            config = ConfigParser()

            config.read(utils.config("postgres.ini"))

            if database_type == constants.DatabaseEnum.LOCAL:
                self._con = psycopg2.connect(**dict(config.items("postgres-local")))

            elif database_type == constants.DatabaseEnum.LOCAL2HEROKU:
                self._con = psycopg2.connect(**dict(config.items("postgres-heroku")))

        self.cur = self._con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    @classmethod
    def get_query(cls, file):
        path = utils.query(file)

        try:
            with open(path, "r") as fh:
                query = fh.read()

                return query

        except OSError as e:
            print(e)

        return None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._con:
            self._con.commit()
            self.cur.close()
            self._con.close()

