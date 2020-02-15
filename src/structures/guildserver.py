import discord

from .guildmember import GuildMember

from src.common.constants import MEMBER_ROLE_ID, MAX_DAYS_NO_UPDATE


class GuildServer:
	def __init__(self, server: discord.Guild):
		self._server = server

		self.members = []
		self.slacking = []

		self._load_members()

	def _load_members(self):
		member_role = discord.utils.get(self._server.roles, id=MEMBER_ROLE_ID)

		for m in self._server.members:
			if member_role not in m.roles:
				continue

			member = GuildMember(m.id, self._server)

			if member.game_stats.has_stats:
				self.members.append(member)

			elif member.slacking():
				self.slacking.append(member)

	def members_sorted(self) -> list:
		return sorted(self.members, key=lambda m: m.game_stats.trophies, reverse=True)

	def create_leaderboard(self):
		members = self.members_sorted()

		# Get the length of the longest username
		longest_name = len(sorted(members, key=lambda mem: len(mem.member.display_name), reverse=True)[0].member.display_name)

		msg = f"```Darkness Family Leaderboard\n"
		msg += f"\n    Username{' ' * (longest_name - 5)}Lvl  Trophies"

		for rank, m in enumerate(members):
			days_ago = m.game_stats.days_since_set()

			member = m.member

			username_length = len(member.display_name)
			username_gap = " " * (longest_name - username_length) + " " * 3

			msg += f"\n#{rank + 1:02d} {member.display_name}{username_gap}{m.game_stats.level:03d}  {m.game_stats.trophies:04d}"
			msg += f"  {days_ago} days ago" if days_ago >= MAX_DAYS_NO_UPDATE else ""

		msg += "```"

		return msg
