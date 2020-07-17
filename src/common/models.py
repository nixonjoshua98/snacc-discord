
class ServersM:
	SELECT_SERVER = "SELECT * FROM servers WHERE server_id=$1 LIMIT 1;"

	INSERT_SERVER = """
	INSERT INTO servers (server_id, prefix, default_role, member_role, display_joins)
	VALUES ($1, $2, $3, $4, $5)
	ON CONFLICT
		DO NOTHING;
	RETURNING *
	"""

	@classmethod
	async def get_server(cls, con, svr: int):
		row = await con.fetchrow(cls.SELECT_SERVER, svr)

		if row is None:
			row = await con.execute(cls.INSERT_SERVER, svr)

		return row

	@classmethod
	async def update(cls, con, server, **kwargs):
		set_values = ", ".join([f"{k}=${i}" for i, k in enumerate(kwargs.keys(), start=2)])

		q = f"UPDATE servers SET {set_values} WHERE server_id=$1;"

		await con.execute(q, server, *list(kwargs.values()))


class ArenaStatsM:
	SELECT_USER = "SELECT * FROM arena_stats WHERE user_id = $1 ORDER BY date_set DESC;"

	INSERT_ROW = "INSERT INTO arena_stats (user_id, date_set, level, trophies) VALUES ($1, $2, $3, $4);"
	DELETE_ROW = "DELETE FROM arena_stats WHERE user_id = $1 AND date_set = $2;"

	SELECT_ALL_USERS_LATEST = """
	SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies
	FROM arena_stats
	ORDER BY user_id, date_set DESC;
	"""

	SELECT_LEADERBOARD = """
	SELECT * FROM (
		SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies
		FROM arena_stats
		WHERE user_id = ANY ($1)
		ORDER BY user_id, date_set DESC
		) q
	ORDER BY trophies DESC;
	"""


class BankM:
	SELECT_RICHEST = "SELECT * FROM bank ORDER BY money DESC;"

	INSERT_ROW = """
	INSERT INTO bank (user_id) VALUES ($1) 
	ON CONFLICT 
		DO NOTHING 
	RETURNING *;
	"""

	SELECT_ROW = "SELECT * FROM bank WHERE user_id = $1 LIMIT 1;"

	ADD_MONEY = """
	INSERT INTO bank (user_id, money) VALUES ($1, $2)
	ON CONFLICT (user_id) DO
		UPDATE SET money = GREATEST(0, bank.money + $2);
	"""

	SUB_MONEY = """
	INSERT INTO bank (user_id, money) VALUES ($1, $2)
	ON CONFLICT (user_id) DO
		UPDATE SET money = GREATEST(0, bank.money - $2);
	"""

	@classmethod
	async def get_row(cls, con, user_id: int):
		row = await con.fetchrow(cls.SELECT_ROW, user_id)

		if row is None:
			row = await con.fetchrow(cls.INSERT_ROW, user_id)

		return row


class HangmanM:
	SELECT_MOST_WINS = "SELECT user_id, wins FROM hangman ORDER BY wins DESC LIMIT 15;"

	ADD_WIN = """
	INSERT INTO hangman (user_id, wins) VALUES ($1, 1)
	ON CONFLICT (user_id) DO
		UPDATE SET wins = hangman.wins + 1;
	"""


class EmpireM:
	SELECT_ALL = "SELECT * FROM empire;"
	SELECT_ROW = "SELECT * FROM empire WHERE user_id = $1 LIMIT 1;"
	INSERT_ROW = "INSERT INTO empire (user_id, name) VALUES ($1, $2);"

	UPDATE_NAME = "UPDATE empire SET name = $2 WHERE user_id = $1;"

	UPDATE_LAST_INCOME = "UPDATE empire SET last_income = $2 WHERE user_id = $1;"

	@classmethod
	async def add_unit(cls, con, user_id: int, unit, amount: int):
		await con.execute(f"UPDATE empire SET {unit.db_col} = {unit.db_col} + $2 WHERE user_id = $1;", user_id, amount)

	@classmethod
	async def sub_unit(cls, con, user_id: int, unit, amount: int):
		await con.execute(f"UPDATE empire SET {unit.db_col} = {unit.db_col} - $2 WHERE user_id = $1;", user_id, amount)
