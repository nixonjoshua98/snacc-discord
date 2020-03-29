import os

from snacc_bot.common.database import DBConnection


def path(file_name: str) -> str:
    return os.path.join(os.getcwd(), "snacc_bot", "resources", file_name)


def execute_query(file: str):
    """ Execute query which expects no return """
    with DBConnection() as con:
        query = con.get_query(file)

        con.cur.execute(query)
