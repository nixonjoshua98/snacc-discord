
class ServersSQL:
    SELECT_SERVER = "SELECT * FROM servers WHERE server_id=$1;"

    INSERT_SERVER = "INSERT INTO servers (server_id, prefix, default_role, member_role) " \
                    "VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING;"

    UPDATE_PREFIX = "UPDATE servers SET prefix = $2 WHERE server_id=$1;"
    UPDATE_MEMBER_ROLE = "UPDATE servers SET member_role = $2 WHERE server_id=$1;"
    UPDATE_DEFAULT_ROLE = "UPDATE servers SET default_role = $2 WHERE server_id=$1;"


class ArenaStatsSQL:
    SELECT_USER_LATEST = ("SELECT DISTINCT ON (user_id) date_set, level, trophies "
                          "FROM arena_stats "
                          "WHERE user_id = $1 "
                          "ORDER BY user_id, date_set DESC;")

    SELECT_ALL_USERS_LATEST = ("SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies "
                               "FROM arena_stats "
                               "ORDER BY user_id, date_set DESC;")

    SELECT_LEADERBOARD = ("SELECT * FROM"
                          "("
                          "SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies "
                          "FROM arena_stats "
                          "WHERE user_id = ANY ($1) "
                          "ORDER BY user_id, date_set DESC"
                          ") q "
                          "ORDER BY trophies DESC;")

    SELECT_USER = ("SELECT user_id, date_set, level, trophies "
                   "FROM arena_stats "
                   "WHERE user_id = $1 "
                   "ORDER BY date_set DESC;")

    INSERT_ROW = "INSERT INTO arena_stats (user_id, date_set, level, trophies) VALUES ($1, $2, $3, $4);"

    DELETE_ROW = "DELETE FROM arena_stats WHERE user_id = $1 AND date_set = $2;"


class HangmanSQL:
    SELECT_HANGMAN_LEADERBOARD = "SELECT user_id, wins FROM hangman ORDER BY wins DESC;"

    ADD_WIN = ("INSERT INTO hangman (user_id, wins) VALUES ($1, 1) "
               "ON CONFLICT (user_id) DO "
               "UPDATE SET wins = hangman.wins + 1;")

