import requests
import json
import os

from datetime import datetime

from src.common import FileReader
from src.common import constants


JSON_URL_LOOKUP = {
	"game_stats.json": "https://api.myjson.com/bins/1d98rq",
	"coins.json": "https://api.myjson.com/bins/fb9yk"
}

headers = {
	"Content-Type": "application/json"
}


def download_file(file: str):
	url = JSON_URL_LOOKUP.get(file, None)

	if url is None:
		return

	response = requests.get(url, headers=headers)

	if response.status_code == requests.codes.ok:
		with FileReader(file) as f:
			f.overwrite(response.json())

		print(f"Downloaded '{file}'")

	else:
		print(f"Failed to download '{file}'")


def upload_file(file: str) :
	debug_mode = os.getenv("DEBUG", False)

	url = JSON_URL_LOOKUP.get(file, None)

	if not debug_mode and url is not None:
		with FileReader(file) as f:
			data = f.data()

		requests.put(url, headers=headers, data=json.dumps(data))

		print(f"Uploaded '{file}'")


def backup_background_task(backup_cooldown: int):
	for f in JSON_URL_LOOKUP:
		path = os.path.join(constants.RESOURCES_DIR, f)

		modified_date = datetime.fromtimestamp(os.path.getmtime(path))

		time_since_update = datetime.today() - modified_date

		if time_since_update.total_seconds() <= backup_cooldown:
			upload_file(f)


def backup_all_files():
	for f in JSON_URL_LOOKUP:
		upload_file(f)


def download_all_files():
	for f in JSON_URL_LOOKUP:
		download_file(f)
