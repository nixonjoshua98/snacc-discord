import json
import os

from . import constants


def read_json(file_name: str):
	p = os.path.join(constants.RESOURCES_DIR, file_name)

	with open(p, "r") as f:
		data = json.load(f)

	return data


def write_json(file_name: str, new_data):
	p = os.path.join(constants.RESOURCES_DIR, file_name)

	with open(p, "w") as f:
		json.dump(new_data, f)