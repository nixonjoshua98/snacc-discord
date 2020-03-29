import os
import psycopg2
import psycopg2.extras

from configparser import ConfigParser


class DBConnection:
    _query_cache = {}

    def __init__(self):
        config = ConfigParser()

        config.read("./snacc_bot/postgres.ini")

        #os.environ["DATABASE_URL"] = "postgres://axuloidgiwznzu:80b3caeeabe61dd86c60659b7defb446a21fda960435d94a5b628c92ee079dde@ec2-46-137-84-173.eu-west-1.compute.amazonaws.com:5432/df1828oi2tg2c9"

        if os.getenv("DEBUG", False):
            self._con = psycopg2.connect(**dict(config.items("postgres")))
        else:
            self._con = psycopg2.connect(os.getenv("DATABASE_URL", None), sslmode="require")

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
