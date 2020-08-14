
class TableModel(type):
	_TABLE, _PK = None, None

	async def set(self, con, id_, **kwargs):
		set_values = ", ".join([f"{k}=${i}" for i, k in enumerate(kwargs.keys(), start=2)])

		q = f"UPDATE {self._TABLE} SET {set_values} WHERE {self._PK}=$1;"

		await con.execute(q, id_, *list(kwargs.values()))

	async def increment(self, con, id_, *, field, amount):
		q = f"UPDATE {self._TABLE} SET {field} = GREATEST(0, {field} + $2) WHERE {self._PK} = $1;"

		await con.execute(q, id_, amount)

	async def decrement(self, con, id_, *, field, amount):
		q = f"UPDATE {self._TABLE} SET {field} = GREATEST(0, {field} - $2) WHERE {self._PK} = $1;"

		await con.execute(q, id_, amount)

	async def decrement_many(self, con, id_, data: dict):
		q = f"UPDATE {self._TABLE} SET "
		q += ", ".join((f"{field} = GREATEST(0, {field} - ${i})" for i, field in enumerate(data, start=2)))
		q += f" WHERE {self._PK} = $1;"

		await con.execute(q, id_, *list(data.values()))

	async def fetchrow(self, con, id_: int, *, insert: bool = True):
		select = f"SELECT * FROM {self._TABLE} WHERE {self._PK}=$1 LIMIT 1;"

		row = await con.fetchrow(select, id_)

		if insert and row is None:
			insert = f"""
			INSERT INTO {self._TABLE} ({self._PK})
			VALUES ($1)
			ON CONFLICT ({self._PK})
				DO NOTHING
			RETURNING *
			"""

			row = await con.fetchrow(insert, id_)

		return row

	async def fetchall(self, con, *, limit: int = None):
		return await con.fetch(f"SELECT * FROM {self._TABLE}{f' LIMIT {limit}' if limit is not None else ''};")

	async def delete(self, con, id_: int):
		q = f"DELETE FROM {self._TABLE} WHERE {self._PK}=$1;"

		await con.execute(q, id_)


class PlayerM(metaclass=TableModel):
	_TABLE, _PK = "players", "player_id"

	SELECT_TOP_VOTERS = f"""
	SELECT player_id, votes
	FROM {_TABLE}
	ORDER BY votes DESC
	LIMIT 100;
	"""


class ServersM(metaclass=TableModel):
	_TABLE, _PK = "servers", "server_id"


class ArenaStatsM:
	INSERT_ROW = "INSERT INTO arena_stats (user_id, date_set, level, trophies) VALUES ($1, $2, $3, $4);"
	DELETE_ROW = "DELETE FROM arena_stats WHERE user_id = $1 AND date_set = $2;"

	SELECT_USER = "SELECT * FROM arena_stats WHERE user_id = $1 ORDER BY date_set DESC;"

	SELECT_LATEST_MEMBERS = """
	SELECT DISTINCT ON (user_id) user_id, date_set, level, trophies
	FROM arena_stats
	WHERE user_id = ANY ($1)
	ORDER BY user_id, date_set DESC
	"""

	SELECT_LEADERBOARD = f"SELECT * FROM ({SELECT_LATEST_MEMBERS}) q ORDER BY trophies DESC;"


class BankM(metaclass=TableModel):
	_TABLE, _PK = "bank", "user_id"

	SELECT_RICHEST = "SELECT * FROM bank ORDER BY money DESC LIMIT 100;"


class HangmanM:
	SELECT_MOST_WINS = "SELECT * FROM hangman ORDER BY wins DESC LIMIT 100;"

	ADD_WIN = """
	INSERT INTO hangman (user_id, wins) VALUES ($1, 1)
	ON CONFLICT (user_id) DO
		UPDATE SET wins = hangman.wins + 1;
	"""


class PopulationM(metaclass=TableModel):
	_TABLE, _PK = "population", "population_id"


class EmpireM(metaclass=TableModel):
	_TABLE, _PK = "empire", "empire_id"


class UserUpgradesM(metaclass=TableModel):
	_TABLE, _PK = "user_upgrades", "user_upgrades_id"


class QuestsM(metaclass=TableModel):
	_TABLE, _PK = "quests", "quest_id"

	INSERT_ROW = f"""
	INSERT INTO {_TABLE} ({_PK}, quest_num, success_rate, date_started)  
	VALUES ($1, $2, $3, $4) 
	ON CONFLICT (quest_id) 
		DO NOTHING
	RETURNING * 
	"""

	@classmethod
	async def fetchrow(cls, con, id_, **_):
		return await con.fetchrow(f"SELECT * FROM {cls._TABLE} WHERE {cls._PK}=$1 LIMIT 1;", id_)


class RemindersM(metaclass=TableModel):
	_TABLE, _PK = "reminders", "reminder_id"

	SELECT_ALL = f"SELECT * FROM {_TABLE};"
	DELETE_ROW = f"DELETE FROM {_TABLE} WHERE {_PK} = $1;"

	INSERT_ROW = f"""
	INSERT INTO {_TABLE} (user_id, channel_id, remind_start, remind_end)  
	VALUES ($1, $2, $3, $4) 
	RETURNING * 
	"""

	@classmethod
	async def fetchrow(cls, con, id_, **_):
		return await con.fetchrow(f"SELECT * FROM {cls._TABLE} WHERE {cls._PK}=$1 LIMIT 1;", id_)
