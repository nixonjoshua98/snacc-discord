
from src.common.queries import BankSQL

from src.structs.leaderboard import TextLeaderboardBase


class MoneyLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(MoneyLeaderboard, self).__init__(
            title="Richest Players",
            query=BankSQL.SELECT_LEADERBOARD,
            columns=["money"],
            order_col="money",
            max_rows=15
        )