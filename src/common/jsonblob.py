import requests
import json
import os

from src.common import FileReader
from src.common.constants import JSON_URL_LOOKUP


def download_all():
	for file, url in JSON_URL_LOOKUP.items():
		if download_file(file):
			print(f"'{file}' downloaded from '{url}'")


def download_file(file: str):
	url = JSON_URL_LOOKUP.get(file, None)

	if url is not None:
		headers = requests.utils.default_headers()

		r = requests.get(url, headers=headers)

		data_dict = json.loads(r.json())

		if r.status_code == 200:
			with FileReader(file) as f:
				f.overwrite(data_dict)

			return r.json()

	print(f"'{file}' download failed since URL is None")


def upload_file(file: str):
	debug_mode = os.getenv("DEBUG", False)

	url = JSON_URL_LOOKUP.get(file, None)

	if url is not None and not debug_mode:
		with FileReader(file) as f:
			data = f.data()

		headers = requests.utils.default_headers()

		r = requests.put(url, headers=headers, json=json.dumps(data))

		return r.status_code == requests.codes.ok

	print(f"'{file}' was not uploaded due to being in debug mode ")
