
from src.common import data_reader


class FileReader:
	def __init__(self, file_name):
		self._file_name = file_name

		self._loaded_file = None
		self._file_updated = False

	# - SETS -

	def increment(self, key: str, value, default_val: int = 0):
		self._file_updated = True
		self._loaded_file[str(key)] = self._loaded_file.get(str(key), default_val) + value

	def decrement(self, key: str, value, default_val: int = 0):
		self._file_updated = True
		self._loaded_file[str(key)] = self._loaded_file.get(str(key), default_val) - value

	def set(self, key: str, value):
		self._file_updated = True
		self._loaded_file[str(key)] = value

	# - GETS -

	def get(self, key: str, default_val=None):
		return self._loaded_file.get(str(key), default_val)

	def data(self):
		return self._loaded_file

	# - SPECIAL METHODS -

	def __enter__(self):
		self._loaded_file = data_reader.read_json(self._file_name)

		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if self._file_updated:
			data_reader.write_json(self._file_name, self._loaded_file)