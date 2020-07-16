

class BankM:
	USER_ID, MONEY = "user_id", "money"

	SELECT_RICHEST = "SELECT * FROM bank ORDER BY money DESC;"

	INSERT_ROW = "INSERT INTO bank (user_id) VALUES ($1) ON CONFLICT DO NOTHING RETURNING *;"
	SELECT_ROW = "SELECT * FROM bank WHERE user_id = $1 LIMIT 1;"

	ADD_MONEY = (
		"INSERT INTO bank (user_id, money) VALUES ($1, $2) "
		"ON CONFLICT (user_id) DO "
		"UPDATE SET money = bank.money + $2;"
	)

	SUB_MONEY = (
		"INSERT INTO bank (user_id, money) VALUES ($1, $2) "
		"ON CONFLICT (user_id) DO "
		"UPDATE SET money = bank.money - $2;"
	)

	@classmethod
	async def get_row(cls, con, user_id: int):
		row = await con.fetchrow(cls.SELECT_ROW, user_id)

		if row is None:
			row = await con.fetchrow(cls.INSERT_ROW, user_id)

		return row


class HangmanM:
	USER_ID, WINS = "user_id", "wins"

	SELECT_MOST_WINS = "SELECT user_id, wins FROM hangman ORDER BY wins DESC LIMIT 15;"

	ADD_WIN = (
		"INSERT INTO hangman (user_id, wins) VALUES ($1, 1) "
		"ON CONFLICT (user_id) DO "
		"UPDATE SET wins = hangman.wins + 1;"
	)


class EmpireM:
	USER_ID, NAME, LAST_INCOME = "user_id", "name", "last_income"

	FARMERS, BUTCHERS, COOKS, BAKERS, WINEMAKERS = "farmers", "butchers", "cooks", "bakers", "winemakers"

	SELECT_ALL = "SELECT * FROM empire;"
	SELECT_ROW = "SELECT * FROM empire WHERE user_id = $1 LIMIT 1;"

	INSERT_ROW = "INSERT INTO empire (user_id, name) VALUES ($1, $2);"

	UPDATE_NAME = "UPDATE empire SET name = $2 WHERE user_id = $1;"

	@classmethod
	async def add_unit(cls, con, unit, user_id: int):
		await con.execute(f"UPDATE empire SET {unit.db_col} = {unit.db_col} + $2 WHERE user_id = $1;", user_id)