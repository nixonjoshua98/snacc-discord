import datetime as dt


class _Object:
	__slots__ = ()

	def __str__(self):
		return f"{self.__class__.__name__}({', '.join((f'{k}={getattr(self, k)}' for k in self.__slots__))})"


class PlayerObject(_Object):

	@staticmethod
	def get_last_active(timestamp):
		now = dt.datetime.utcnow()

		update_time = dt.datetime.utcfromtimestamp(timestamp)

		return dt.timedelta(seconds=int((now - update_time).total_seconds()))


class LeaderboardPlayer(PlayerObject):
	__slots__ = ("name", "rank", "level", "rating", "guild", "last_active", "guild_xp", "total_guild_xp")

	def __init__(self, **kwargs):

		self.name = kwargs["name"]
		self.rank = kwargs["position"] + 1
		self.level = kwargs["level"]
		self.rating = kwargs["rating"]

		self.guild_xp = kwargs["guildXp"]
		self.total_guild_xp = kwargs["rollingGuildXp"]

		self.last_active = self.get_last_active(kwargs["lastUpdateTime"])

		self.guild = kwargs.get("guildName", "N/A")


class LeaderboardGuild(_Object):
	__slots__ = ("name", "leader", "rank", "rating", "size",  "guild_xp", "total_guild_xp")

	def __init__(self, **kwargs):
		self.name = kwargs["name"]
		self.rank = kwargs["position"] + 1
		self.rating = kwargs["rating"]
		self.size = kwargs["membersCount"]

		self.leader = kwargs.get("leaderName", "N/A")

		self.guild_xp = kwargs["guildXp"]
		self.total_guild_xp = kwargs["rollingGuildXp"]
