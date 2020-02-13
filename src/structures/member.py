from .member_game_stats import MemberGameStats


class Member:
	def __init__(self, _id: int):
		self._id = _id

		self.game_stats = MemberGameStats(_id=_id)

	def update_game_stats(self, *, level: int, trophies: int):
		return self.game_stats.update(level=level, trophies=trophies)
