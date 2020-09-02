import os

from motor.motor_asyncio import AsyncIOMotorClient


class MongoClient(AsyncIOMotorClient):
	def __init__(self):
		super(MongoClient, self).__init__(os.getenv("MONGO_CON_STR"))
