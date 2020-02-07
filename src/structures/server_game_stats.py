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

		for m in members:
			if not m.has_set_stats():
				continue

			days_ago = m.days_since_set()

			msg += f"\n#{rank } {m.display_name} "

			if days_ago > 0:
				msg += f"({days_ago} day{'' if days_ago == 1 else 's'} ago)"

			msg += f"\n\tLvl: {m.level} Trophies: {m.trophies}"

			rank += 1

		msg += "```"

		return msg
