import discord

from .member_game_stats import GameStats


class GuildMember:
	def __init__(self, _id: int, server: discord.Guild):
		self._id = _id

		self.member = server.get_member(user_id=self._id)
		self.game_stats = GameStats(_id=_id)

	def update_game_stats(self, *, level: int, trophies: int):
		return self.game_stats.update(level=level, trophies=trophies)

	def slacking(self) -> bool:
		return self.game_stats.slacking()

	def create_stat_embed(self) -> discord.Embed:
		embed = discord.Embed(
			title=f"Member: {self.member.display_name}",
			description=f"Member Stats",
			color=0xff8000
		)

		stats_list = self.game_stats.serialize("%d/%m/%Y")

		for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
			embed.add_field(name=txt, value=stats_list[i])

		return embed