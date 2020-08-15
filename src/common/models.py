
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


class PopulationM(metaclass=TableModel):
	_TABLE, _PK = "population", "population_id"
