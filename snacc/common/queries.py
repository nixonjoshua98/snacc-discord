
class ServersSQL:
    DEFAULT_ROW = {"prefix": "!", "entry_role": 0, "member_role": 0}

    # SELECT
    SELECT_SERVER = "SELECT * FROM servers WHERE server_id=$1;"

    # INSERT
    INSERT_SERVER = "INSERT INTO servers (server_id, prefix, default_role, member_role) " \
                    "VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING;"

    # UPDATE
    UPDATE_PREFIX = "UPDATE servers SET prefix = $2 WHERE server_id=$1;"
    UPDATE_MEMBER_ROLE = "UPDATE servers SET member_role = $2 WHERE server_id=$1;"
    UPDATE_DEFAULT_ROLE = "UPDATE servers SET default_role = $2 WHERE server_id=$1;"


class ArenaStatsSQL:
    # SELECT
    SELECT_USER_LATEST = ("SELECT DISTINCT ON (user_id) date_set, level, trophies "
                          "FROM arena_stats "
                          "WHERE user_id = $1 "
                          "ORDER BY user_id, date_set DESC;")

    SELECT_ALL_USERS_LATEST = ("SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies "
                               "FROM arena_stats "
                               "ORDER BY user_id, date_set DESC;")

    SELECT_TROPHY_LEADERBOARD = ("SELECT * FROM"
                                 "("
                                 "SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies "
                                 "FROM arena_stats "
                                 "ORDER BY user_id, date_set DESC"
                                 ") q "
                                 "ORDER BY trophies DESC;")

    SELECT_LEADERBOARD = ("SELECT * FROM"
                          "("
                          "SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies "
                          "FROM arena_stats "
                          "WHERE user_id = ANY ($1) "
                          "ORDER BY user_id, date_set DESC"
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

    # DELETE
    DELETE_ROW = "DELETE FROM arena_stats " \
                 "WHERE user_id = $1 AND date_set = $2;"


class HangmanSQL:
    # SELECT
    SELECT_HANGMAN_LEADERBOARD = "SELECT user_id, wins FROM hangman ORDER BY wins DESC;"

    # INSERT
    ADD_WIN = ("INSERT INTO hangman (user_id, wins) VALUES ($1, 1) "
               "ON CONFLICT (user_id) DO "
               "UPDATE SET wins = hangman.wins + 1;")


class PrivateChannelsSQL:
    # SELECT
    SELECT_EXPIRING_CHANNELS = "SELECT server_id, channel_id, owner_id, lifetime " \
                               "FROM private_channels " \
                               "WHERE can_expire = True;"

    SELECT_CHANNEL = "SELECT * FROM private_channels WHERE server_id = $1 AND channel_id = $2;"

    # INSERT
    INSERT_CHANNEL = "INSERT INTO private_channels (server_id, channel_id, owner_id, lifetime, can_expire) " \
                     "VALUES($1, $2, $3, $4, True);"

    # DELETE
    DELETE_ROW = "DELETE FROM private_channels WHERE server_id = $1 AND channel_id = $2;"

    # Update
    UPDATE_LIFETIME = "UPDATE private_channels " \
                      "SET lifetime = private_channels.lifetime + $3 " \
                      "WHERE server_id = $1 AND channel_id = $2;"

