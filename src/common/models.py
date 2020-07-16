

class Bank:
	USER_ID, MONEY = "user_id", "money"

	SELECT_RICHEST = "SELECT * FROM bank ORDER BY money DESC;"

	INSERT_ROW = "INSERT INTO bank (user_id) VALUES ($1) ON CONFLICT DO NOTHING RETURNING *;"
	SELECT_ROW = "SELECT * FROM bank WHERE user_id = $1 LIMIT 1;"

	@classmethod
	def get_row(cls, con, user_id: int):
		row = await con.fetchrow(cls.SELECT_ROW, user_id)

		if row is None:
			row = await con.fetchrow(cls.INSERT_ROW, user_id)

		return row
