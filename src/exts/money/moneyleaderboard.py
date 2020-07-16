
from src.common.models import BankM

from src.structs.leaderboard import TextLeaderboardBase


class MoneyLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(MoneyLeaderboard, self).__init__(
            title="Richest Players",
            query=BankM.SELECT_RICHEST,
            columns=[BankM.MONEY],
            order_col=BankM.MONEY,
            max_rows=15
        )
