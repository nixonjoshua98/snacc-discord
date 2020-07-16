
from src.common.queries import ArenaStatsSQL

from src.structs.leaderboard import TextLeaderboardBase


class TrophyLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(TrophyLeaderboard, self).__init__(
            title="Trophy Leaderboard",
            query=ArenaStatsSQL.SELECT_LEADERBOARD,
            columns=["level", "trophies"],
            order_col="trophies"
        )

    async def execute_query(self, ctx) -> list:
        svr_config = await ctx.bot.get_server(ctx.guild)

        role = ctx.guild.get_role(svr_config["member_role"])

        results = await ctx.bot.pool.fetch(self.query, tuple(member.id for member in role.members))

        return results
