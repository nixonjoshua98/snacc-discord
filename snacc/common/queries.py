
class ServersSQL:
    DEFAULT_ROW = {"prefix": "!", "entryRole": 0, "memberRole": 0}

    # CREATE
    CREATE_TABLE = "CREATE table IF NOT EXISTS servers (" \
                   "serverID BIGINT PRIMARY KEY," \
                   "defaultRole BIGINT," \
                   "memberRole BIGINT," \
                   "prefix VARCHAR(255)" \
                   ");"

    # SELECT
    SELECT_SERVER = "SELECT * FROM servers WHERE serverID=$1;"

    # INSERT
    INSERT_SERVER = "INSERT INTO servers (serverID, prefix, entryRole, memberRole) " \
                    "VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING;"

    # UPDATE
    UPDATE_PREFIX = "UPDATE servers SET prefix = $2 WHERE serverID=$1;"
    UPDATE_MEMBER_ROLE = "UPDATE servers SET memberRole = $2 WHERE serverID=$1;"
    UPDATE_DEFAULT_ROLE = "UPDATE servers SET defaultRole = $2 WHERE serverID=$1;"


class ArenaStatsSQL:

    # CREATE
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS arena_stats (" \
                   "arena_stat_id SERIAL," \
                   "user_id BIGINT," \
                   "date_set TIMESTAMP," \
                   "level SMALLINT," \
                   "trophies SMALLINT" \
                   ");"

    # SELECT
    SELECT_USER_LATEST = ("SELECT DISTINCT ON (user_id) date_set, level, trophies "
                          "FROM arena_stats "
                          "WHERE user_id = $1 "
                          "ORDER BY user_id, date_set DESC;")

    SELECT_HIGHEST_TROPHIES = ("SELECT * FROM ("
                               "SELECT DISTINCT ON (user_id) user_id, level, trophies "
                               "FROM arena_stats "
                               "ORDER BY user_id, trophies DESC"
                               ") q "
                               "ORDER BY trophies DESC;")

    # SELECT
    SELECT_USER = ("SELECT user_id, date_set, level, trophies "
                   "FROM arena_stats "
                   "WHERE user_id = $1 "
                   "ORDER BY date_set DESC;")

    # INSERT
    INSERT_ROW = "INSERT INTO arena_stats (user_id, date_set, level, trophies) " \
                 "VALUES ($1, $2, $3, $4);"


class HangmanSQL:
    # CREATE
    CREATE_TABLE = ("CREATE table IF NOT EXISTS hangman ("
                    "user_id BIGINT PRIMARY KEY, "
                    "wins INTEGER;")

    # SELECT
    SELECT_ALL = "SELECT userID, wins FROM hangman;"
    SELECT_BEST = "SELECT userID, wins FROM hangman ORDER BY wins DESC LIMIT 10"

    # INSERT
    ADD_WIN = ("INSERT INTO hangman (userID, wins) VALUES ($1, 1) "
               "ON CONFLICT (userID) DO "
               "UPDATE SET wins = hangman.wins + 1;")
