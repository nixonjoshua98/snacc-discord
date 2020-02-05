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

			stats = GuildMember(_id=m.id, display_name=m.display_name)

			if stats.has_stats():
				self.append(stats)

	def sort_by_trophies(self):
		self.sort(key=lambda m: m.stats.trophies, reverse=True)

	def get_members_no_updates(self, days: int):
		return [m for m in self if m.days_since_stat_set() >= days]

	def create_leaderboard(self, *, sort_by: str):
		if sort_by == "trophies":
			self.sort_by_trophies()

		msg = f"```Darkness Family Leaderboard\n"

		for rank, member in enumerate(self):
			stats = member.stats
			days_ago = member.days_since_stat_set()

			msg += f"\n#{rank + 1} {member.display_name} "

			if days_ago > 0:
				msg += f"({days_ago} day{'' if days_ago == 1 else 's'} ago)"

			msg += f"\n\tLvl: {stats.level} Trophies: {stats.trophies}"

			rank += 1

		msg += "```"

		return msg



