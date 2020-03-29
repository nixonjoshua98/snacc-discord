import os
import psycopg2
import psycopg2.extras

from configparser import ConfigParser


class DBConnection:
    _query_cache = {}

    def __init__(self):
        config = ConfigParser()

        config.read("./snacc_bot/postgres.ini")

        self._con = psycopg2.connect(**dict(config.items("postgres")))
        self.cur = self._con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    @classmethod
    def get_query(cls, file, cache: bool = True):
        if cls._query_cache.get(file, None) is not None:
            return cls._query_cache[file]

        path = os.path.join(os.getcwd(), "snacc_bot", "queries", file)

        try:
            with open(path, "r") as fh:
                query = fh.read()

                if cache:
                    cls._query_cache[file] = query

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
