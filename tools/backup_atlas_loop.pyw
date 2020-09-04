import time
import os
import json
import pymongo

import datetime as dt

from bson import ObjectId

BACKUP_PATH = "D:\\Program Files\\OneDrive\\Databases\\atlas\\snacc"

db = "snaccV2"


def get_data_from_atlas():
    def get_con_str():
        with open(os.path.join(os.getcwd(), "con_str.txt")) as fh:
            s = fh.read()

        return s

    con_str = get_con_str()

    atlas_data = dict()

    with pymongo.MongoClient(con_str) as client:
        for col in client[db].list_collection_names():
            atlas_data[col] = list(client[db][col].find())

    return atlas_data


def write_data_to_json(atlas_data):
    def default(s):
        if isinstance(s, (dt.date, dt.datetime)):
            return s.isoformat()

        elif isinstance(s, ObjectId):
            return str(s)

    now = dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    with open(f"{BACKUP_PATH}\\{now}.json", "w") as fh:
        json.dump(atlas_data, fh, default=default, indent=1)


def write_to_local_database(atlas_data):
    with pymongo.MongoClient() as client:
        for col in atlas_data:
            if atlas_data[col]:
                client[db][col].drop()

                client[db][col].insert_many(atlas_data[col])


while True:
    data = get_data_from_atlas()

    write_to_local_database(data)

    write_data_to_json(data)

    print(".", end="")

    time.sleep(3_600)
