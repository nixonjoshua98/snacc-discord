
from .arenastats import ArenaStats


def setup(bot):
	bot.add_cog(ArenaStats(bot))
