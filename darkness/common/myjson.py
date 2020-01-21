
import requests
import json
import os

from darkness.common import constants
from darkness.common import data_reader


def _get_file_url(*, file: str = None):
	return constants.JSON_URL_LOOKUP.get(file, None)


def get_json(*, file: str = None, cache: bool = True):
	url = _get_file_url(file=file)

	if url is None:
		raise Exception(f"{__name__}")

	headers = {"Content-Type": "application/json"}

	response = requests.get(url, headers=headers)

	data = {}

	if response.status_code == requests.codes.ok:
		data = response.json()

		if cache:
			data_reader.write_json(file, **data)

	return data


def upload_json(*, file: str):
	headers = {
		"Content-Type": "application/json"
	}

	url = constants.JSON_URL_LOOKUP.get(file, None)

	if url is not None:
		response = requests.put(url, headers=headers, data=json.dumps(data_reader.read_json(file)))

		return response.status_code == requests.codes.ok

	return False

