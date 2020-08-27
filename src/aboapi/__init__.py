import json
import httpx
import gzip
import base64


class _Object:
	__slots__ = ()

	def __str__(self):
		return f"{self.__class__.__name__}({', '.join((f'{k}={getattr(self, k)}' for k in self.__slots__))})"


class Player(_Object):
	__slots__ = ("name", "rank", "level", "rating", "guild")

	def __init__(self, **kwargs):
		self.name = kwargs["name"]
		self.rank = kwargs["position"] + 1
		self.level = kwargs["level"]
		self.rating = kwargs["rating"]

		self.guild = kwargs.get("guildName")


class Guild(_Object):
	__slots__ = ("name", "leader", "rank", "rating", "size")

	def __init__(self, **kwargs):
		self.name = kwargs["name"]
		self.rank = kwargs["position"] + 1
		self.leader = kwargs["leaderName"]
		self.rating = kwargs["rating"]
		self.size = kwargs["membersCount"]


class API:

	@classmethod
	async def get_players(cls, *, pos, count):
		data = {"purpose": "get", "position": pos, "count": count, "global": {}}

		if (resp := await cls._send_request("leaderboard", data)) is not None:
			return [Player(**user) for user in resp["users"]]

		return None

	@classmethod
	async def get_guilds(cls, *, pos, count):
		data = {"purpose": "getGuilds", "position": pos, "count": count, "global": {}}

		if (resp := await cls._send_request("leaderboard", data)) is not None:
			return [Guild(**guild) for guild in resp["guilds"]]

		return None

	@classmethod
	async def get_player(cls, name):
		data = {"purpose": "get", "position": -1, "count": 30, "name": name, "global": {}}

		return await cls._get_one(name, data, key="users", class_=Player)

	@classmethod
	async def get_guild(cls, name):
		data = {"purpose": "getGuilds", "position": -1, "count": 30, "name": name, "global": {}}

		return await cls._get_one(name, data, key="guilds", class_=Guild)

	@classmethod
	async def _get_one(cls, name, data, *, key, class_):
		if (resp := await cls._send_request("leaderboard", data)) is not None:
			for user in resp[key]:
				inst = class_(**user)

				if inst.name.lower() == name.lower():
					return inst

		return None

	@classmethod
	async def _send_request(cls, path, data) -> dict:
		url = f"http://174.138.116.133:8443/api/{path}"

		data_bytes = json.dumps(data).encode("utf-8")

		data_compressed = gzip.compress(data_bytes)

		put_data = base64.b64encode(data_compressed).decode("utf-8")

		async with httpx.AsyncClient() as client:
			r = await client.put(url, data=put_data)

		if r.status_code == httpx.codes.ok:
			resp = base64.b64decode(r.content)

			resp_uncompressed = gzip.decompress(resp)

			return json.loads(resp_uncompressed.decode("utf-8"))

		return None
