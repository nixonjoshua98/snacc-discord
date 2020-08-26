import os

from motor.motor_asyncio import AsyncIOMotorClient


class MongoClient(AsyncIOMotorClient):
	def __init__(self):
		super(MongoClient, self).__init__(os.getenv("MONGO_CON_STR"))

		self.db = self.snacc

	def find(self, col, kwargs=None):
		return self.db[col].find(kwargs or dict())

	async def bulk_write(self, con, requests):
		return await self.db[con].bulk_write(requests)

	async def insert_one(self, col, kwargs):
		return await self.db[col].insert_one(kwargs)

	async def find_one(self, col, kwargs):
		return (await self.db[col].find_one(kwargs)) or dict()

	async def delete_one(self, col, kwargs):
		return await self.db[col].delete_one(kwargs)

	async def delete_many(self, col, kwargs):
		return await self.db[col].delete_many(kwargs)

	async def increment_one(self, col, query, kwargs):
		return await self.db[col].update_one(query, {"$inc": kwargs}, upsert=True)

	async def increment_many(self, col, query, kwargs):
		return await self.db[col].update_many(query, {"$inc": kwargs}, upsert=True)

	async def update_one(self, col, query, update):
		return await self.db[col].update_one(query, update, upsert=True)

	async def set_one(self, col, query, kwargs):
		return await self.db[col].update_one(query, {"$set": kwargs}, upsert=True)

	async def decrement_one(self, col, query, kwargs):
		row = await self.find_one(col, query)

		decre = {k: -v if (row.get(k, 0) - v) >= 0 else row.get(k, 0) for k, v in kwargs.items()}

		return await self.db[col].update_one(query, {"$inc": decre}, upsert=True)
