import requests
import json
import os

from datetime import datetime
from src.common import data_reader
from src.common import constants


def download_file(file: str):
	url = constants.JSON_URL_LOOKUP.get(file, None)
	headers = {"Content-Type": "application/json"}
	response = requests.get(url, headers=headers)
	if response.status_code == requests.codes.ok:
		data = response.json()
		data_reader.write_json(file, data)
		print(f"Downloaded '{file}'")

	else:
		print(f"Failed to download '{file}'")


def upload_file(file: str):
	debug_mode = os.getenv("DEBUG", False)

	if not debug_mode:
		url = constants.JSON_URL_LOOKUP.get(file, None)
		headers = {"Content-Type": "application/json"}
		if url is not None:
			data = data_reader.read_json(file)
			requests.put(url, headers=headers, data=json.dumps(data))
			print(f"Uploaded '{file}'")

	else:
		print(f"Uploading {file} failed due to being in DEBUG mode")


def backup_all_files():
	for f in constants.JSON_URL_LOOKUP:
		path = os.path.join(constants.RESOURCES_DIR, f)

		modified_date = datetime.fromtimestamp(os.path.getmtime(path))

		time_since_update = datetime.today() - modified_date

		if time_since_update.total_seconds() <= constants.BACKUP_DELAY:
			upload_file(f)
