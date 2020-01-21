import os
import json

from darkness.common.constants import RESOURCES_DIR


def read_json(file_name: str):
	p = os.path.join(RESOURCES_DIR, file_name)

	with open(p, "r") as f:
		data = json.load(f)

	return data


def update_key(file_name: str, *, key: str, value):
	p = os.path.join(RESOURCES_DIR, file_name)
	
	data = read_json(file_name)

	data[key] = value

	with open(p, "w") as f:
		json.dump(data, f)


def remove_key(file_name: str, *, key: str):
	p = os.path.join(RESOURCES_DIR, file_name)

	data = read_json(file_name)

	data[key] = None

	del data[key]

	write_json(file_name, data)


def write_json(file_name: str, new_data):
	p = os.path.join(RESOURCES_DIR, file_name)

	with open(p, "w") as f:
		json.dump(new_data, f)