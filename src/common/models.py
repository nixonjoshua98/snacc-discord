
class TableModel:
	_TABLE, _PK = None, None

	@classmethod
	async def set(cls, con, _id, **kwargs):
		set_values = ", ".join([f"{k}=${i}" for i, k in enumerate(kwargs.keys(), start=2)])

		q = f"UPDATE {cls._TABLE} SET {set_values} WHERE {cls._PK}=$1;"

		await con.execute(q, _id, *list(kwargs.values()))


class PlayerM:
	_TABLE, _PK = "player", "player_id"

	SELECT_ROW = f"SELECT * FROM {_TABLE} WHERE {_PK} = $1 LIMIT 1;"

	SET_LAST_LOGIN = """
	INSERT INTO player (player_id, last_login)
	VALUES ($1, $2)
	ON CONFLICT (player_id) DO
		UPDATE SET last_login = $2 WHERE player.player_id = $1;	
	"""


class ServersM(TableModel):
	_TABLE, _PK = "servers", "server_id"

	SELECT_SERVER = "SELECT * FROM servers WHERE server_id=$1 LIMIT 1;"

	INSERT_SERVER = """
	INSERT INTO servers (server_id)
	VALUES ($1)
	ON CONFLICT (server_id)
		DO NOTHING
	RETURNING *
	"""

	@classmethod
	async def get_server(cls, con, svr: int):
		row = await con.fetchrow(cls.SELECT_SERVER, svr)

		if row is None:
			row = await con.fetchrow(cls.INSERT_SERVER, svr)

		return row

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
	ON CONFLICT (user_id)
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
		UPDATE SET money = GREATEST(0, bank.money - $2) ;
	"""

	ADD_BTC = """
	INSERT INTO bank (user_id, BTC) VALUES ($1, $2)
	ON CONFLICT (user_id) DO
		UPDATE SET BTC = GREATEST(0, bank.BTC + $2);
	"""

	SUB_BTC = """
	INSERT INTO bank (user_id, BTC) VALUES ($1, $2)
	ON CONFLICT (user_id) DO
		UPDATE SET BTC = GREATEST(0, bank.BTC - $2) ;
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


class PopulationM:
	SELECT_ROW = "SELECT * FROM population WHERE population_id = $1 LIMIT 1;"
	INSERT_ROW = """
	INSERT INTO population (population_id)
	VALUES ($1)
	ON CONFLICT (population_id)
		DO NOTHING
	RETURNING *;
	"""

	SELECT_ALL = "SELECT * FROM population;"

	@classmethod
	async def add_unit(cls, con, user_id: int, unit, amount: int):
		q = f"UPDATE population SET {unit.db_col} = {unit.db_col} + $2 WHERE population_id = $1;"

		await con.execute(q, user_id, amount)

	@classmethod
	async def sub_unit(cls, con, user_id: int, unit, amount: int):
		q = f"UPDATE population SET {unit.db_col} = {unit.db_col} - $2 WHERE population_id = $1;"

		await con.execute(q, user_id, amount)

	@classmethod
	async def get_row(cls, con, user_id: int):
		row = await con.fetchrow(cls.SELECT_ROW, user_id)

		if row is None:
			row = await con.fetchrow(cls.INSERT_ROW, user_id)

		return row


class EmpireM(TableModel):
	_TABLE, _PK = "empire", "empire_id"

	SELECT_ROW = "SELECT * FROM empire WHERE empire_id = $1 LIMIT 1;"
	INSERT_ROW = "INSERT INTO empire (empire_id) VALUES ($1) RETURNING empire_id;"

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


class UserUpgradesM:
	SELECT_ROW = "SELECT * FROM user_upgrades WHERE user_upgrades_id=$1 LIMIT 1;"

	INSERT_ROW = """
	INSERT INTO user_upgrades (user_upgrades_id)  
	VALUES ($1) 
	ON CONFLICT (user_upgrades_id) 
		DO NOTHING
	RETURNING * 
	"""

	@classmethod
	async def get_row(cls, con, id_: int):
		row = await con.fetchrow(cls.SELECT_ROW, id_)

		if row is None:
			row = await con.fetchrow(cls.INSERT_ROW, id_)

		return row

	@classmethod
	async def add_upgrade(cls, con, user_id: int, unit, amount: int):
		q = f"UPDATE user_upgrades SET {unit.db_col} = {unit.db_col} + $2 WHERE user_upgrades_id = $1;"

		await con.execute(q, user_id, amount)
