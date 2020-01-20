
import requests
import json
import os

from darkness.common import constants
from darkness.common import data_reader


def upload(file: str):
	headers = {
		"Content-Type": "application/json"
	}

	url = constants.JSON_URL_LOOKUP.get(file, None)

	if url is not None:
		response = requests.put(url, headers=headers, data=json.dumps(data_reader.read_json(file)))

		return response.status_code == requests.codes.ok

	return False


def upload_all():
	ok = True

	for k in constants.JSON_URL_LOOKUP:
		if not upload(k):
			ok = False

	return ok


def download(file: str):
	headers = {
		"Content-Type": "application/json"
	}

	url = constants.JSON_URL_LOOKUP.get(file, None)

	if url is not None:
		response = requests.get(url, headers=headers)

		if response.status_code == requests.codes.ok:
			data = response.json()

			data_reader.write_json_keys(file, **data)

		return response.status_code == requests.codes.ok

	return False


def download_all():
	ok = True

	for k in constants.JSON_URL_LOOKUP:
		if not download(k):
			ok = False

	return ok