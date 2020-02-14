import discord

from src.common.constants import MEMBER_ROLE_ID

from .player_game_stats import PlayerGameStats


class ServerGameStats:
	STAT_SET_COOLDOWN = 3

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
		return [m for m in self._members if not m.has_set_stats() or m.days_since_set() >= self.STAT_SET_COOLDOWN]

	def create_leaderboard(self,):
		members = self.sorted_by_trophies()

		# Get the length of the longest username
		longest_name = len(sorted(members, key=lambda mem: len(mem.display_name), reverse=True)[0].display_name)

		msg = f"```Darkness Family Leaderboard\n"
		msg += f"\n    Username{' ' * (longest_name - 5)}Lvl  Trophies"

		for rank, m in enumerate(members):
			if not m.has_set_stats():
				continue

			days_ago = m.days_since_set()

			username_length = len(m.display_name)
			username_gap = " " * (longest_name - username_length) + " " * 3

			msg += f"\n#{rank + 1:02d} {m.display_name}{username_gap}{m.level:03d}  {m.trophies:04d}"
			msg += f"  {days_ago} days ago" if days_ago >= self.STAT_SET_COOLDOWN else ""

		msg += "```"

		return msg
