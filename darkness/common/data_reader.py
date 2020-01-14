import os
import json

from darkness.common.constants import RESOURCES_DIR


def read_json(file_name: str):
	p = os.path.join(RESOURCES_DIR, file_name)

	with open(p, "r") as f:
		data = json.load(f)

	return data
