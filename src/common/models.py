
class TableModel:
	_TABLE, _PK = None, None

	SELECT_ROW = None
	INSERT_ROW = None

	@classmethod
	async def set(cls, con, _id, **kwargs):
		set_values = ", ".join([f"{k}=${i}" for i, k in enumerate(kwargs.keys(), start=2)])

		q = f"UPDATE {cls._TABLE} SET {set_values} WHERE {cls._PK}=$1;"

		await con.execute(q, _id, *list(kwargs.values()))

	@classmethod
	async def increment(cls, con, _id, *, field, amount):
		q = f"UPDATE {cls._TABLE} SET {field} = GREATEST(0, {field} + $2) WHERE {cls._PK} = $1;"

		await con.execute(q, _id, amount)

	@classmethod
	async def decrement(cls, con, _id, *, field, amount):
		q = f"UPDATE {cls._TABLE} SET {field} = GREATEST(0, {field} - $2) WHERE {cls._PK} = $1;"

		await con.execute(q, _id, amount)

	@classmethod
	async def fetchrow(cls, con, id_: int):
		row = await con.fetchrow(cls.SELECT_ROW, id_)

		if row is None:
			row = await con.fetchrow(cls.INSERT_ROW, id_)

		return row


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

	@classmethod
	async def blacklist_channels(cls, con, svr: int, channels):
		""" Blacklist a list of channels. """

		row = await con.fetchrow("SELECT blacklisted_channels FROM servers WHERE server_id=$1 LIMIT 1;", svr)

		blacklisted = row["blacklisted_channels"]
		blacklisted = list(set(blacklisted + channels))

		await cls.set(con, svr, blacklisted_channels=blacklisted)

	@classmethod
	async def whitelist_channels(cls, con, svr: int, channels):
		""" Remove an list of channels from the blacklist list. """

		row = await con.fetchrow("SELECT blacklisted_channels FROM servers WHERE server_id=$1 LIMIT 1;", svr)

		blacklisted = row["blacklisted_channels"]
		blacklisted = list(set(blacklisted) - set(channels))

		await cls.set(con, svr, blacklisted_channels=blacklisted)

	@classmethod
	async def blacklist_modules(cls, con, svr: int, channels):
		""" Blacklist a list of modules. """

		row = await con.fetchrow("SELECT blacklisted_cogs FROM servers WHERE server_id=$1 LIMIT 1;", svr)

		blacklisted = row["blacklisted_cogs"]
		blacklisted = list(set(blacklisted + channels))

		await cls.set(con, svr, blacklisted_cogs=blacklisted)

	@classmethod
	async def whitelist_modules(cls, con, svr: int, channels):
		""" Remove an list of modules from the blacklist list. """

		row = await con.fetchrow("SELECT blacklisted_cogs FROM servers WHERE server_id=$1 LIMIT 1;", svr)

		blacklisted = row["blacklisted_cogs"]
		blacklisted = list(set(blacklisted) - set(channels))

		await cls.set(con, svr, blacklisted_cogs=blacklisted)


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

	SET_LAST_LOGIN = "UPDATE empire SET last_login = $2 WHERE empire_id = $1;"

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
