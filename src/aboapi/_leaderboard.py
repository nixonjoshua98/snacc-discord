
from src.aboapi._classes import LeaderboardGuild, LeaderboardPlayer

from src.aboapi._utils import _send_request


class _Leaderboard:

	@classmethod
	async def get_player(cls, name):
		data = {"purpose": "get", "position": -1, "count": 30, "name": name, "global": {}}

		if (resp := await _send_request("leaderboard", data)) is not None:
			for user in resp["users"]:
				inst = LeaderboardPlayer(**user)

				if inst.name.lower() == name.lower():
					return inst

		return None

	@classmethod
	async def get_players(cls, *, pos, count):
		data = {"purpose": "get", "position": pos, "count": count, "global": {}}

		if (resp := await _send_request("leaderboard", data)) is not None:
			return [LeaderboardPlayer(**user) for user in resp["users"]]

		return None

	@classmethod
	async def get_guild(cls, name):
		data = {"purpose": "getGuilds", "position": -1, "count": 30, "name": name, "global": {}}

		if (resp := await _send_request("leaderboard", data)) is not None:
			for user in resp["guilds"]:
				inst = LeaderboardGuild(**user)

				if inst.name.lower() == name.lower():
					return inst

		return None

	@classmethod
	async def get_guilds(cls, *, pos, count):
		data = {"purpose": "getGuilds", "position": pos, "count": count, "global": {}}

		if (resp := await _send_request("leaderboard", data)) is not None:
			return [LeaderboardGuild(**guild) for guild in resp["guilds"]]

		return None
