import pymongo

client = pymongo.MongoClient(input("Connection: "))

data = dict()

for col in client.snacc.list_collection_names():
    data[col] = list(client.snacc[col].find())


client = pymongo.MongoClient()

for k, v in data.items():
    client.snacc[k].drop()
    
    if v:
        client.snacc[k].insert_many(v)
