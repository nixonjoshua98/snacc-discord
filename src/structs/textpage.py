

class TextPage:
	def __init__(self, title=None, headers=None, footer=None):
		self.title = title
		self.footer = footer
		self.headers = headers

		self.rows = []

	def get(self):
		widths = self._get_max_widths()

		s = [(self.title or "") + "\n", self._pad_row(self.headers, widths)]

		for row in self.rows:
			s.append(self._pad_row(row, widths))

		if self.footer is not None:
			s.append("-")
			s.append(self._pad_row(self.footer, widths) if isinstance(self.footer, (list, tuple)) else self.footer)

		return "```c++\n" + '\n'.join(s) + "```"

	def _get_max_widths(self):
		widths = [0 for _ in range(max(map(len, [self.headers] + self.rows)))]

		for ls in [self.headers] + self.rows:
			for i, cell in enumerate(ls):
				widths[i] = max(widths[i], len(str(cell)))

		return widths

	def _pad_row(self, row, widths):
		return " ".join(f"{col}{' ' * (widths[i] - len(str(col)))}" for i, col in enumerate(row))

	def set_title(self, title):
		self.title = title

	def add_row(self, ls):
		self.rows.append(ls)

	def add_rows(self, *ls):
		for row in ls:
			self.add_row(row)

	def set_headers(self, ls):
		self.headers = ls

	def set_footer(self, footer):
		self.footer = footer

