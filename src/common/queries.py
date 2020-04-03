
UPDATE_PREFIX_SQL = """
INSERT INTO server_config (serverID, prefix) VALUES (%s, %s)
ON CONFLICT (serverID) DO UPDATE
SET prefix = excluded.prefix;
"""

UPDATE_ABO_STATS_SQL = """
INSERT INTO abo (userID, lvl, trophies, dateSet) VALUES (%s, %s, %s, %s)
ON CONFLICT (userID) DO UPDATE
SET lvl = excluded.lvl, trophies = excluded.trophies, dateSet = excluded.dateSet;
"""

UPDATE_SVR_CHANNELS_SQL = """
INSERT INTO server_config (serverID, channels) VALUES (%s, %s)
ON CONFLICT (serverID) DO UPDATE
SET channels = excluded.channels;
"""

UPDATE_SVR_ROLES_SQL = """
INSERT INTO server_config (serverID, roles) VALUES (%s, %s)
ON CONFLICT (serverID) DO UPDATE
SET roles = excluded.roles;
"""