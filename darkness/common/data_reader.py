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

	with open(p, "r") as f:
		data = json.load(f)

	data[key] = value

	with open(p, "w") as f:
		json.dump(data, f)


def write_json(file_name: str, **kwargs):
	p = os.path.join(RESOURCES_DIR, file_name)

	data = read_json(file_name)

	for k, w in kwargs.items():
		data[k] = w

	with open(p, "w") as f:
		json.dump(data, f)


def remove_json_key(file_name: str, key: str):
	p = os.path.join(RESOURCES_DIR, file_name)

	data = read_json(file_name)

	data[key] = []

	del data[key]

	with open(p, "w") as f:
		json.dump(data, f)


def append_json_keys(file_name: str, key: str, ls: list):
	p = os.path.join(RESOURCES_DIR, file_name)

	data = read_json(file_name)

	value = data.get(key, [])

	value.append(ls)

	data[key] = value

	with open(p, "w") as f:
		json.dump(data, f)