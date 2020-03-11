import multiprocessing.dummy
import requests
import json
import os

from datetime import datetime

from src.common import FileReader
from src.common import constants


JSON_URL_LOOKUP = {
	"game_stats.json": "https://api.myjson.com/bins/1d98rq",
	"coins.json": "https://api.myjson.com/bins/fb9yk",
	"pet_stats.json": "https://api.myjson.com/bins/leyri",
	"server_settings.json": "https://api.myjson.com/bins/f4aku"
}

headers = {
	"Content-Type": "application/json"
}

def _output_results(results: list, method: str):
	for i, k in enumerate(JSON_URL_LOOKUP):
		if results[i] is True:
			print(f"{method}ed {k}")

		elif results[i] is False:
			print(f"Failed to {method} {k}")


def download_file(file: str):
	url = JSON_URL_LOOKUP.get(file, None)

	if url is None:
		return

	response = requests.get(url, headers=headers)

	if response.status_code == requests.codes.ok:
		with FileReader(file) as f:
			f.overwrite(response.json())

	return response.status_code == requests.codes.ok


def upload_file(file: str) :
	debug_mode = os.getenv("DEBUG", False)

	url = JSON_URL_LOOKUP.get(file, None)

	if url is None:
		return

	if not debug_mode:
		with FileReader(file) as f:
			data = f.data()

		response = requests.put(url, headers=headers, data=json.dumps(data))

		return response.status_code == requests.codes.ok



def backup_background_task(backup_cooldown: int):
	def upload(f):
		path = os.path.join(constants.RESOURCES_DIR, f)

		modified_date = datetime.fromtimestamp(os.path.getmtime(path))

		if (datetime.today() - modified_date).total_seconds() < backup_cooldown:
			return upload_file(f)

	with multiprocessing.dummy.Pool(processes=4) as pool:
		results = pool.map(upload, list(JSON_URL_LOOKUP.keys()))

	_output_results(results, "upload")


def backup_all_files():
	with multiprocessing.dummy.Pool(processes=4) as pool:
		results = pool.map(upload_file, list(JSON_URL_LOOKUP.keys()))

	_output_results(results, "upload")


def download_all_files():
	with multiprocessing.dummy.Pool(processes=4) as pool:
		results = pool.map(download_file, list(JSON_URL_LOOKUP.keys()))

	_output_results(results, "download")
