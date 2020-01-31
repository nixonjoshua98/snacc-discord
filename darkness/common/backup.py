import requests
import json

from darkness.common import data_reader
from darkness.common import constants


def download_file(file: str):
	url = constants.JSON_URL_LOOKUP.get(file, None)

	headers = {"Content-Type": "application/json"}

	response = requests.get(url, headers=headers)

	if response.status_code == requests.codes.ok:
		data = response.json()

		data_reader.write_json(file, data)

		print(f"Downloaded '{file}'")


def upload_file(file: str):
	url = constants.JSON_URL_LOOKUP.get(file, None)

	headers = {"Content-Type": "application/json"}

	if url is not None:
		data = data_reader.read_json(file)

		requests.put(url, headers=headers, data=json.dumps(data))

		print(f"Uploaded '{file}'")
