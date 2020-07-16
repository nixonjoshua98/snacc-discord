
from src.common.models import HangmanM

from src.structs.leaderboard import TextLeaderboardBase


class HangmanLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(HangmanLeaderboard, self).__init__(
            title="Top Hangman Players", query=HangmanM.SELECT_MOST_WINS,
            columns=[HangmanM.WINS], order_col=HangmanM.WINS
        )
