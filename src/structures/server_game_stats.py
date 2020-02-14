import discord

from src.common.constants import MEMBER_ROLE_ID

from .player_game_stats import PlayerGameStats


class ServerGameStats:
	def __init__(self, guild: discord.Guild):
		self._guild = guild
		self._members = []

		self._read_stats()

	def _read_stats(self):
		member_role = discord.utils.get(self._guild.roles, id=MEMBER_ROLE_ID)

		for m in self._guild.members:
			if member_role not in m.roles:
				continue

			member = PlayerGameStats(self._guild, m.id)

			self._members.append(member)

	def sorted_by_trophies(self) -> list:
		members = [m for m in self._members if m.has_set_stats()]

		return sorted(members, key=lambda m: m.trophies, reverse=True)

	def get_slacking_members(self):
		return [m for m in self._members if not m.has_set_stats() or m.days_since_set() >= 3]

	def create_leaderboard(self, *, sort_by: str):
		members = self._members

		if sort_by == "trophies":
			members = self.sorted_by_trophies()

		msg = f"```Darkness Family Leaderboard\n"

		rank = 1

		longest_name = len(sorted(members, key=lambda mem: len(mem.display_name), reverse=True)[0].display_name)

		for m in members:
			if not m.has_set_stats():
				continue

			username_length = len(m.display_name)

			username_gap = ' ' * (longest_name + 3 - username_length)
			level_gap = " " * 2
			rank_gap = " " * 2

			msg += f"\n#{rank:02d}{rank_gap}|{m.display_name}{username_gap}|{m.level:03d}{level_gap}|{m.trophies:04d}|"

			rank += 1

		msg += "```"

		return msg
