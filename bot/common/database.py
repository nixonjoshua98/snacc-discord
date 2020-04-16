import os
import psycopg2
import psycopg2.extras

from configparser import ConfigParser

from bot.common import BotConstants, DatabaseEnum


class DBConnection:
    def __init__(self, target_database: DatabaseEnum = None):
        """
        :param target_database: Decide which database to connect to
        """
        target_database = BotConstants.DATABASE if target_database is None else target_database

        if target_database == DatabaseEnum.HEROKU:
            # Connect to Heroku database using the DATABASE_URL stored in the environment variables
            self._con = psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

        else:
            config = ConfigParser()

            config.read("postgres.ini")

            section = "postgres" if target_database == DatabaseEnum.LOCAL else "postgres-heroku"

            self._con = psycopg2.connect(**dict(config.items(section)))

        self.cur = self._con.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    def __enter__(self):
        """ Context manager entry point """
        return self

    def __exit__(self, *args):
        """ Context manager exit point """
        self.close()

    def close(self):
        """ Close the connection if it is still open"""
        if self._con:
            self._con.commit()
            self.cur.close()
            self._con.close()

