import os

from motor.motor_asyncio import AsyncIOMotorClient


class MongoClient(AsyncIOMotorClient):
	def __init__(self):
		super(MongoClient, self).__init__(os.getenv("MONGO_CON_STR"))

		self.db = self.snacc

	def find(self, col, kwargs=None): return self.db[col].find(kwargs or dict())

	async def insert_one(self, col, kwargs): return await self.db[col].insert_one(kwargs)

	async def find_one(self, col, kwargs): return await self.db[col].find_one(kwargs)

	async def delete_one(self, col, kwargs): return await self.db[col].delete_one(kwargs)
