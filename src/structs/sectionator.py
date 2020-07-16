
class _Section:
	pass


class Sectionator:
	def __init__(self, title=None, footer=None, headers=None):
		self.title = title
		self.footer = footer
		self.headers = [] if headers is None else headers

		self.sections = []

	def get(self) -> str:
		return "```c++\n" + "The page" + "```"

	def set_title(self, title: str): self.title = title

	def set_footer(self, footer: str): self.footer = footer

	def set_headers(self, headers: list): self.headers = headers

	def add_row(self, ls, index):
		""" Add row to a section. """

	def _get_max_widths(self) -> int:
		return 0

	def _pad_row(self, row, widths) -> str:
		return "Row"
