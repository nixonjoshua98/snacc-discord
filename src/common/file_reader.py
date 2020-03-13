import os
import json

from src.common.constants import RESOURCES_DIR



class FileReader:
	def __init__(self, file_name):
		self._file_name = os.path.join(RESOURCES_DIR, file_name)

		self._loaded_file = None
		self._file_updated = False

	# - SETS -

	def overwrite(self, data: dict):
		self._file_updated = True
		self._loaded_file = data

	def set(self, key: str, value):
		self._file_updated = True
		self._loaded_file[str(key)] = value

	def set_inner_key(self, key: str, inner_key: str, value):
		key, inner_key = str(key), str(inner_key)
		self._file_updated = True
		data = self._loaded_file.get(key, {})
		data[inner_key] = value
		self._loaded_file[key] = data

	def remove(self, key: str):
		self._file_updated = True
		self._loaded_file.pop(key, None)

	# - GETS -

	def get(self, key: str, default_val=None):
		return self._loaded_file.get(str(key), default_val)

	def get_inner_key(self, key: str, inner_key: str, default_value=None):
		key, inner_key = str(key), str(inner_key)

		return self._loaded_file.get(key, {}).get(inner_key, default_value)

	def data(self):
		return self._loaded_file

	# - SPECIAL METHODS -

	def __enter__(self):
		with open(self._file_name, "r") as f:
			self._loaded_file = json.load(f)

		return self

	def __exit__(self, exc_type, exc_value, exc_traceback):
		if self._file_updated:
			with open(self._file_name, "w") as f:
				json.dump(self._loaded_file, f)
