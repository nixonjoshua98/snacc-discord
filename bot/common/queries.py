
class ServersSQL:
    TABLE = "CREATE table IF NOT EXISTS servers (" \
            "serverID BIGINT PRIMARY KEY," \
            "entryRole BIGINT," \
            "prefix VARCHAR(255)" \
            ");"

    INSERT_SERVER = "INSERT INTO servers (serverID, prefix, entryRole) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING;"
    UPDATE_PREFIX = "UPDATE servers SET prefix = $2 WHERE serverID=$1;"
    SELECT_SERVER = "SELECT * FROM servers WHERE serverID=$1;"

    UPDATE_ENTRY_ROLE = "UPDATE servers SET entryRole = $2 WHERE serverID=$1;"


class BankSQL:
    DEFAULT_ROW = {"money": 500}

    TABLE = "CREATE table IF NOT EXISTS bank (" \
            "userID BIGINT PRIMARY KEY, " \
            "money BIGINT" \
            ");"

    SELECT_RICHEST = "SELECT * FROM bank ORDER BY money DESC LIMIT 10"

    INSERT_USER = "INSERT INTO bank (userID, money) VALUES ($1, $2) ON CONFLICT DO NOTHING;"
    SELECT_USER = "SELECT * FROM bank WHERE userID=$1;"

    SET_MONEY = "UPDATE bank SET money = $2 WHERE userID = $1;"


class HangmanSQL:
    TABLE = "CREATE table IF NOT EXISTS hangman (" \
            "userID BIGINT PRIMARY KEY, " \
            "wins INTEGER" \
            ");"

    SELECT_BEST = "SELECT * FROM hangman ORDER BY wins DESC LIMIT 10"

    ADD_WIN = "INSERT INTO hangman (userID, wins) VALUES ($1, 1) " \
              "ON CONFLICT (userID) DO " \
              "UPDATE SET wins = hangman.wins + 1;"


class AboSQL:
    TABLE = "CREATE table IF NOT EXISTS abo (" \
            "userID BIGINT PRIMARY KEY, " \
            "lvl SMALLINT, " \
            "trophies SMALLINT, " \
            "dateSet TIMESTAMP" \
            ");"

    SELECT_BEST = "SELECT * FROM abo ORDER BY trophies DESC;"

    SELECT_ALL = "SELECT * FROM abo;"

    UPDATE_USER = "INSERT INTO abo (userID, lvl, trophies, dateSet) VALUES ($1, $2, $3, $4) " \
                  "ON CONFLICT (userID) DO UPDATE " \
                  "SET lvl = excluded.lvl, trophies = excluded.trophies, dateSet = excluded.dateSet;"
