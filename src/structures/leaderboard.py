

class Leaderboard:
	def __init__(self, title: str, file: str, columns: list, sort_func=None):
		self._title = title
		self._file = file
		self._columns = columns
		self._col_headers = {}
		self._col_funcs = {}
		self._sort_func = sort_func

	def add_column(self, col: str, name: str = None, func=None):
		self._columns.append(col)

		if name is not None:
			self.rename_columns(col, name)

		self._col_funcs[col] = func

	def rename_columns(self, col: str, name: str):
		if col not in self._columns:
			raise Exception(f"Column '{col}' is not present in the leaderboard")

		self._col_headers[col] = name

