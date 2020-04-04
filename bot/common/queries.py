

class ServerConfigSQL:
    SELECT_ALL = "SELECT * FROM server_config;"

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
    SELECT_ALL = "SELECT * FROM abo;"

    SELECT_USER = "SELECT * FROM abo WHERE userID = %s;"

    UPDATE = "INSERT INTO abo (userID, lvl, trophies, dateSet) VALUES (%s, %s, %s, %s) " \
             "ON CONFLICT (userID) DO UPDATE " \
             "SET lvl = excluded.lvl, trophies = excluded.trophies, dateSet = excluded.dateSet;"


class CoinsSQL:
    SELECT_ALL = "SELECT * FROM coins;"

    SELECT_USER = "SELECT * FROM coins WHERE userID = %s;"

    UPDATE = "INSERT INTO coins (userID, balance) VALUES (%s, %s) " \
             "ON CONFLICT (userID) DO UPDATE " \
             "SET balance = excluded.balance;"


INCREMENT_COINS = """
INSERT INTO coins (userID, balance) VALUES (%s, %s)
ON CONFLICT (userID) DO UPDATE
SET balance = coins.balance + excluded.balance;
"""

DECREMENT_COINS = """
INSERT INTO coins (userID, balance) VALUES (%s, %s)
ON CONFLICT (userID) DO UPDATE
SET balance = coins.balance - excluded.balance;
"""

SET_COINS = """
INSERT INTO coins (userID, balance) VALUES (%s, %s)
ON CONFLICT (userID) DO UPDATE
SET balance = excluded.balance;
"""


# - - - SERVER_CONFIG QUERIES - - -

SELECT_ALL_CONFIG = "SELECT * FROM server_config;"

UPDATE_PREFIX_SQL = """
INSERT INTO server_config (serverID, prefix) VALUES (%s, %s)
ON CONFLICT (serverID) DO UPDATE
SET prefix = excluded.prefix;
"""

UPDATE_SVR_CHANNELS_SQL = """
INSERT INTO server_config (serverID, channels) VALUES (%s, %s)
ON CONFLICT (serverID) DO UPDATE
SET channels = excluded.channels;
"""

UPDATE_ENTIRE_SVR_SQL = """
INSERT INTO server_config (serverID, prefix, channels, roles) VALUES (%s, %s, %s, %s)
ON CONFLICT (serverID) DO UPDATE
SET prefix = excluded.prefix, channels = excluded.channels, roles = excluded.roles;
"""

UPDATE_SVR_ROLES_SQL = """
INSERT INTO server_config (serverID, roles) VALUES (%s, %s)
ON CONFLICT (serverID) DO UPDATE
SET roles = excluded.roles;
"""

# - - - ABO QUERIES - - -

SELECT_ALL_ABO = "SELECT * FROM abo;"

UPDATE_ABO_STATS = """
INSERT INTO abo (userID, lvl, trophies, dateSet) VALUES (%s, %s, %s, %s)
ON CONFLICT (userID) DO UPDATE
SET lvl = excluded.lvl, trophies = excluded.trophies, dateSet = excluded.dateSet;
"""