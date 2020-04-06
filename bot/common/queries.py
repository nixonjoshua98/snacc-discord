

class ServerConfigSQL:
    TABLE = "CREATE table IF NOT EXISTS server_config (" \
            "serverID BIGINT PRIMARY KEY, " \
            "prefix VARCHAR(255), " \
            "channels JSON, " \
            "roles JSON" \
            ");"

    SELECT_ALL = "SELECT * FROM server_config;"

    SELECT_SVR = "SELECT * FROM server_config WHERE serverID = %s;"

    UPDATE = "INSERT INTO server_config (serverID, prefix, channels, roles) VALUES (%s, %s, %s, %s) " \
             "ON CONFLICT (serverID) DO UPDATE " \
             "SET prefix = excluded.prefix, channels = excluded.channels, roles = excluded.roles;"

    UPDATE_PREFIX = "INSERT INTO server_config (serverID, prefix) VALUES (%s, %s) " \
                    "ON CONFLICT (serverID) DO UPDATE " \
                    "SET prefix = excluded.prefix;"

    UPDATE_ROLES = "INSERT INTO server_config (serverID, roles) VALUES (%s, %s) " \
                   "ON CONFLICT (serverID) DO UPDATE " \
                   "SET roles = excluded.roles;"

    UPDATE_CHANNELS = "INSERT INTO server_config (serverID, channels) VALUES (%s, %s) " \
                      "ON CONFLICT (serverID) DO UPDATE " \
                      "SET channels = excluded.channels;"


class AboSQL:
    TABLE = "CREATE table IF NOT EXISTS abo (" \
            "userID BIGINT PRIMARY KEY, " \
            "lvl SMALLINT, " \
            "trophies SMALLINT, " \
            "dateSet TIMESTAMP" \
            ");"

    SELECT_ALL = "SELECT * FROM abo;"

    SELECT_USER = "SELECT * FROM abo WHERE userID = %s;"

    UPDATE = "INSERT INTO abo (userID, lvl, trophies, dateSet) VALUES (%s, %s, %s, %s) " \
             "ON CONFLICT (userID) DO UPDATE " \
             "SET lvl = excluded.lvl, trophies = excluded.trophies, dateSet = excluded.dateSet;"


class CoinsSQL:
    TABLE = "CREATE table IF NOT EXISTS coins (" \
            "userID BIGINT PRIMARY KEY, " \
            "balance BIGINT" \
            ");"

    SELECT_ALL = "SELECT * FROM coins;"

    SELECT_USER = "SELECT * FROM coins WHERE userID = %s;"

    UPDATE = "INSERT INTO coins (userID, balance) VALUES (%s, %s) " \
             "ON CONFLICT (userID) DO UPDATE " \
             "SET balance = excluded.balance;"

    INCREMENT = "INSERT INTO coins (userID, balance) VALUES (%s, %s) " \
                "ON CONFLICT (userID) DO UPDATE " \
                "SET balance = coins.balance + excluded.balance;"

    DECREMENT = "INSERT INTO coins (userID, balance) VALUES (%s, %s) " \
                "ON CONFLICT (userID) DO UPDATE " \
                "SET balance = coins.balance - excluded.balance;"


class FishSQL:
    pass


class MinigamesSQL:
    TABLE = "CREATE table IF NOT EXISTS minigames (" \
            "userID BIGINT PRIMARY KEY, " \
            "timerWins INTEGER" \
            ");"

    SELECT_ALL_TIMER_WINS = "SELECT userID, timerWins FROM minigames;"

    UPDATE_TIMER_WINS = "INSERT INTO minigames (userID, timerWins) VALUES (%s, 1) " \
                    "ON CONFLICT (userID) DO UPDATE " \
                    "SET timerWins = minigames.timerWins + 1"
