

class TextPage:
	def __init__(self, fixes: str = "```"):
		self.title = None
		self.headers = None
		self.footer = None

		self.fixes = fixes if fixes is not None else ""

		self.rows = []

	def get(self):
		widths = self._get_max_widths()

		s = [(self.title or "") + "\n", self._pad_row(self.headers, widths)]

		for row in self.rows:
			s.append(self._pad_row(row, widths))

		if self.footer is not None:
			if isinstance(self.footer, (list, tuple)):
				s.append("-\n" + self._pad_row(self.footer, widths))
			else:
				s.append("-\n" + self.footer)

		return self.fixes + "\n" + '\n'.join(s) + self.fixes

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

	def set_headers(self, ls):
		self.headers = ls

	def set_footer(self, footer):
		self.footer = footer

