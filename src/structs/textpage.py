
class TextPage:
	def __init__(self, *, title: str, headers: list = None):
		self._title = title
		self._footer = None
		self._headers = headers or []

		self.rows = []

	def get(self):
		widths = self._get_widths()

		s = [self._title + "\n"]

		for i, row in enumerate([self._headers] + self.rows):
			padded_row = self._pad_row(row, widths)

			s.append(padded_row)

		if self._footer is not None:
			s.extend(["-", self._footer])

		return "```\n" + "\n".join(s) + "```"

	def add(self, row: list):
		self.rows.append(list(map(lambda e: str(e), row)))

	def set_headers(self, headers: list):
		self._headers = list(map(lambda e: str(e), headers))

	def set_footer(self, footer):
		self._footer = footer

	def _get_widths(self):
		longest_row = max(map(lambda r: len(r), [self._headers] + self.rows))

		widths = [0 for _ in range(longest_row)]

		for row in [self._headers] + self.rows:
			for i, ele in enumerate(row[:-1]):
				widths[i] = max(widths[i], len(ele))

		return widths

	def _pad_row(self, row, widths):
		s = []

		for i, ele in enumerate(row):
			spaces = ' ' * (widths[i] - len(ele))

			s.append(f"{ele}{spaces}")

		return " ".join(s)
