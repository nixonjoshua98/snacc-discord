import os
import psycopg2
import psycopg2.extras

from configparser import ConfigParser

from src.common import utils


class DBConnection:
    def __init__(self):
        config = ConfigParser()

        config.read(utils.config("postgres.ini"))

        if os.getenv("DEBUG", False):
            self._con = psycopg2.connect(**dict(config.items("postgres")))

        else:
            self._con = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

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

