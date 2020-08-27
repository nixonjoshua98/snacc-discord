

class _Object:
	__slots__ = ()

	def __str__(self):
		return f"{self.__class__.__name__}({', '.join((f'{k}={getattr(self, k)}' for k in self.__slots__))})"


class LeaderboardPlayer(_Object):
	__slots__ = ("name", "rank", "level", "rating", "guild", "last_match")

	def __init__(self, **kwargs):

		self.name = kwargs["name"]
		self.rank = kwargs["position"] + 1
		self.level = kwargs["level"]
		self.rating = kwargs["rating"]

		self.guild = kwargs.get("guildName")


class LeaderboardGuild(_Object):
	__slots__ = ("name", "leader", "rank", "rating", "size")

	def __init__(self, **kwargs):
		self.name = kwargs["name"]
		self.rank = kwargs["position"] + 1
		self.leader = kwargs["leaderName"]
		self.rating = kwargs["rating"]
		self.size = kwargs["membersCount"]
