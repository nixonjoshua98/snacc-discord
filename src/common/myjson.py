import requests
import json
import os

from src.common import FileReader
from src.common.constants import JSON_URL_LOOKUP

headers = {
	"Content-Type": "application/json"
}


def download_all():
	for file, url in JSON_URL_LOOKUP.items():
		if download_file(file) is True:
			print(f"'{file}' downloaded from '{url}'")


def download_file(file: str):
	url = JSON_URL_LOOKUP.get(file, None)

	if url is not None:
		response = requests.get(url, headers=headers)

		if response.status_code == requests.codes.ok:
			with FileReader(file) as f:
				f.overwrite(response.json())

		return response.status_code == requests.codes.ok

	print(f"'{file}' download failed since URL is None")


def upload_file(file: str):
	debug_mode = os.getenv("DEBUG", False)

	url = JSON_URL_LOOKUP.get(file, None)

	if url is not None and not debug_mode:
		with FileReader(file) as f:
			data = f.data()

		response = requests.put(url, headers=headers, data=json.dumps(data))

		return response.status_code == requests.codes.ok

	print(f"'{file}' '{url}' was not uploaded due to being in debug mode ")
