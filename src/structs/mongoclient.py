import os
import pymongo
import funcy


class MongoClient(pymongo.MongoClient):
	def __init__(self, *args, **kwargs):
		super(MongoClient, self).__init__(os.getenv("MONGO_CON_STR"), *args, **kwargs)

	@funcy.print_durations()
	def get_servers(self, *args, **kwargs):
		return tuple(self.snacc.servers.find(*args, **kwargs))

	@funcy.print_durations()
	def update_server(self, _id, *, upsert=False, **kwargs):
		self.snacc.servers.update_one({"_id": _id}, {"$set": kwargs}, upsert=upsert)
