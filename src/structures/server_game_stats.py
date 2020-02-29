import discord

from .player_game_stats import PlayerGameStats

from src.common.constants import MEMBER_ROLE_ID


class ServerGameStats:
	def __init__(self, server: discord.Guild):
		self._server = server

		self.active_members = []
		self.slacking_members = []

		self._load()

	def create_shame_message(self):
		return "**Lacking Activity**\n" + " ".join(tuple(map(lambda m: m.user.mention, self.slacking_members)))

	def create_leaderboard(self):
		self.active_members.sort(key=lambda m: m.trophies, reverse=True)

		name_length = 15

		msg = "```c++\n"

		msg += "Darkness Family Leaderboard\n"
		msg += f"\n    Username{' ' * (name_length - 7)}Lvl Trophies"

		for rank, member in enumerate(self.active_members):
			days_ago = member.days_since_set()

			user = member.user

			username_gap = " " * (name_length - len(user.display_name)) + " "

			msg += f"\n#{rank + 1:02d} {user.display_name[0:name_length]}"
			msg += f"{username_gap}{member.level:03d} {member.trophies:04d}"
			msg += f" {days_ago} days ago" if days_ago >= member.MAX_DAYS_NO_UPDATE else ""

		msg += "```"

		return msg

	def _load(self):
		member_role = discord.utils.get(self._server.roles, id=MEMBER_ROLE_ID)

		for m in self._server.members:
			if member_role not in m.roles:
				continue

			member = PlayerGameStats(m)

			if member.has_stats():
				self.active_members.append(member)

			if member.slacking():
				self.slacking_members.append(member)
