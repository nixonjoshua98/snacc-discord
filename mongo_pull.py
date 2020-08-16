import json
import pymongo

import datetime as dt

from bson import ObjectId

from configparser import ConfigParser

config = ConfigParser()

config.read("config.ini")

# - Load data from the atlas
client = pymongo.MongoClient(config.get("database", "MONGO_CON_STR"))

data = dict()

for col in client.snacc.list_collection_names():
    data[col] = list(client.snacc[col].find())


client.close()
