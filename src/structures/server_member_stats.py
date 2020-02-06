import discord

from src.common import constants

from .guild_member import GuildMember


class ServerMemberStats(list):
	def __init__(self, guild: discord.Guild):
		super().__init__()

		self.guild = guild

		self.read_stats()

	def read_stats(self):
		member_role = discord.utils.get(self.guild.roles, id=constants.MEMBER_ROLE_ID)

		for m in self.guild.members:
			if member_role not in m.roles:
				continue

			member = GuildMember(_id=m.id, display_name=m.display_name)

			self.append(member)

	def sort_by_trophies(self):
		# Sorts the members by trophies, defaults the members who have no saved stats to 0
		self.sort(key=lambda m: m.stats.trophies if m.has_stats() else 0, reverse=True)

	def get_members_no_updates(self, days: int):
		"""
		:param days: Days since update
		:return: List of members who either have never set their stats, or within the past X days.
		"""
		return [m for m in self if not m.has_stats() or m.days_since_stat_set() >= days]

	def create_leaderboard(self, *, sort_by: str):
		if sort_by == "trophies":
			self.sort_by_trophies()

		msg = f"```Darkness Family Leaderboard\n"

		rank = 1

		for member in self:
			# Ignore members who have no set stats
			if not member.has_stats():
				continue

			stats = member.stats
			days_ago = member.days_since_stat_set()

			msg += f"\n#{rank } {member.display_name} "

			if days_ago > 0:
				msg += f"({days_ago} day{'' if days_ago == 1 else 's'} ago)"

			msg += f"\n\tLvl: {stats.level} Trophies: {stats.trophies}"

			rank += 1

		msg += "```"

		return msg



