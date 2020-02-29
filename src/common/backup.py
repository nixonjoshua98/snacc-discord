import requests
import json
import os

from datetime import datetime
from src.common import data_reader
from src.common import constants


JSON_URL_LOOKUP = {
	"game_stats.json": "https://api.myjson.com/bins/1d98rq",
	"coins.json": "https://api.myjson.com/bins/fb9yk"
}

headers = {
	"Content-Type": "application/json"
}

# Backup the files in <JSON_URL_LOOKUP> if the time since last edit is greater than this
MAX_TIME_SINCE_BACKUP = 60 * 3


def download_file(file: str):
	url = JSON_URL_LOOKUP.get(file, None)

	response = requests.get(url, headers=headers)

	if response.status_code == requests.codes.ok:
		data_reader.write_json(file, response.json())

		print(f"Downloaded '{file}'")

	else:
		print(f"Failed to download '{file}'")


def upload_file(file: str) -> bool:
	debug_mode = os.getenv("DEBUG", False)

	if not debug_mode:
		url = JSON_URL_LOOKUP.get(file, None)

		if url is not None:
			page = requests.put(url, headers=headers, data=json.dumps(data_reader.read_json(file)))

			print(f"Uploaded '{file}'")

			return page.status_code == requests.codes.ok

	else:
		""" DEBUG Mode """
		return False


def backup_all_files() -> bool:
	is_ok = True

	for f in JSON_URL_LOOKUP:
		path = os.path.join(constants.RESOURCES_DIR, f)

		modified_date = datetime.fromtimestamp(os.path.getmtime(path))

		time_since_update = datetime.today() - modified_date

		if time_since_update.total_seconds() >= MAX_TIME_SINCE_BACKUP:
			if not upload_file(f):
				is_ok = False

	return is_ok
