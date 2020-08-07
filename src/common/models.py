
class TableModel:
	_TABLE, _PK = None, None

	SELECT_ROW = None
	INSERT_ROW = None

	@classmethod
	async def set(cls, con, id_, **kwargs):
		set_values = ", ".join([f"{k}=${i}" for i, k in enumerate(kwargs.keys(), start=2)])

		q = f"UPDATE {cls._TABLE} SET {set_values} WHERE {cls._PK}=$1;"

		await con.execute(q, id_, *list(kwargs.values()))

	@classmethod
	async def increment(cls, con, id_, *, field, amount):
		q = f"UPDATE {cls._TABLE} SET {field} = GREATEST(0, {field} + $2) WHERE {cls._PK} = $1;"

		await con.execute(q, id_, amount)

	@classmethod
	async def decrement(cls, con, id_, *, field, amount):
		q = f"UPDATE {cls._TABLE} SET {field} = GREATEST(0, {field} - $2) WHERE {cls._PK} = $1;"

		await con.execute(q, id_, amount)

	@classmethod
	async def decrement_many(cls, con, id_, data: dict):
		q = f"UPDATE {cls._TABLE} SET "
		q += ", ".join((f"{field} = GREATEST(0, {field} - ${i})" for i, field in enumerate(data, start=2)))
		q += f" WHERE {cls._PK} = $1;"

		await con.execute(q, id_, *list(data.values()))

	@classmethod
	async def fetchrow(cls, con, id_: int, *, insert: bool = True):
		row = await con.fetchrow(cls.SELECT_ROW, id_)

		if insert and row is None:
			row = await con.fetchrow(cls.INSERT_ROW, id_)

		return row

	@classmethod
	async def delete(cls, con, id_: int):
		q = f"DELETE FROM {cls._TABLE} WHERE {cls._PK}=$1;"

		await con.execute(q, id_)


class ServersM(TableModel):
	_TABLE, _PK = "servers", "server_id"

	SELECT_ROW = "SELECT * FROM servers WHERE server_id=$1 LIMIT 1;"

	INSERT_ROW = """
	INSERT INTO servers (server_id)
	VALUES ($1)
	ON CONFLICT (server_id)
		DO NOTHING
	RETURNING *
	"""


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


class BankM(TableModel):
	_TABLE, _PK = "bank", "user_id"

	SELECT_ROW = "SELECT * FROM bank WHERE user_id = $1 LIMIT 1;"
	INSERT_ROW = """
	INSERT INTO bank (user_id) VALUES ($1) 
	ON CONFLICT (user_id)
		DO NOTHING 
	RETURNING *;
	"""

	SELECT_RICHEST = "SELECT * FROM bank ORDER BY money DESC;"


class HangmanM:
	SELECT_MOST_WINS = "SELECT user_id, wins FROM hangman ORDER BY wins DESC LIMIT 15;"

	ADD_WIN = """
	INSERT INTO hangman (user_id, wins) VALUES ($1, 1)
	ON CONFLICT (user_id) DO
		UPDATE SET wins = hangman.wins + 1;
	"""


class PopulationM(TableModel):
	_TABLE, _PK = "population", "population_id"

	SELECT_ROW = "SELECT * FROM population WHERE population_id = $1 LIMIT 1;"
	INSERT_ROW = """
	INSERT INTO population (population_id)
	VALUES ($1)
	ON CONFLICT (population_id)
		DO NOTHING
	RETURNING *;
	"""

	SELECT_ALL = "SELECT * FROM population;"


class EmpireM(TableModel):
	_TABLE, _PK = "empire", "empire_id"

	SELECT_ROW = "SELECT * FROM empire WHERE empire_id = $1 LIMIT 1;"
	INSERT_ROW = """
	INSERT INTO empire (empire_id) VALUES ($1)
	ON CONFLICT (empire_id)
		DO NOTHING		
	RETURNING *;
	"""

	SELECT_ALL_AND_POPULATION = """
	SELECT * FROM empire 
	INNER JOIN 
		population ON (empire.empire_id = population.population_id);
		"""

	SELECT_ROW_AND_POPULATION = """
	SELECT * FROM empire 
	INNER JOIN 
		population ON (empire.empire_id = population.population_id)
	WHERE empire_id = $1;
		"""


class UserUpgradesM(TableModel):
	_TABLE, _PK = "user_upgrades", "user_upgrades_id"

	SELECT_ROW = "SELECT * FROM user_upgrades WHERE user_upgrades_id=$1 LIMIT 1;"
	INSERT_ROW = """
	INSERT INTO user_upgrades (user_upgrades_id)  
	VALUES ($1) 
	ON CONFLICT (user_upgrades_id) 
		DO NOTHING
	RETURNING * 
	"""


class QuestsM(TableModel):
	_TABLE, _PK = "quests", "quest_id"

	SELECT_ROW = "SELECT * FROM quests WHERE quest_id=$1 LIMIT 1;"
	INSERT_ROW = """
	INSERT INTO quests (quest_id, quest_num, success_rate, date_started)  
	VALUES ($1, $2, $3, $4) 
	ON CONFLICT (quest_id) 
		DO NOTHING
	RETURNING * 
	"""

	@classmethod
	async def fetchrow(cls, con, id_: int, *, insert: bool = True):
		return await super(QuestsM, cls).fetchrow(con, id_, insert=False)
