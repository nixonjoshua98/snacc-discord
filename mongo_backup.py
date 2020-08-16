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

# - Copy the data from the atlas to the local database
client = pymongo.MongoClient()

for k, v in data.items():   
    if v:
        client.snacc[k].drop()
        
        client.snacc[k].insert_many(v)

client.close()


# - Write to JSON
def default(s):
    if isinstance(s, (dt.date, dt.datetime)):
        return s.isoformat()

    elif isinstance(s, ObjectId):
        return str(s)

now = dt.datetime.utcnow().strftime("%Y-%m-%d %H-%M-%S")

with open(f"D:\\Program Files\\OneDrive\\Databases\\atlas\\snacc\\{now}.json", "w") as fh:
    json.dump(data, fh, default=default, indent=1)
