from datetime import datetime
from bot.common import DBConnection, AboSQL, CoinsSQL


class LeaderboardBase:
    def __init__(self, title: str, headers: list, columns: list, **options):
        self._title = title
        self._headers = ["#", "Member"] + headers
        self._columns = columns

        self._size = options.get("size", 10)

        self._leaderboard = ""
        self._max_col_width = 15    # Max column width
        self._update_timer = 15     # Update every 50 mins
        self._last_updated = None

    def get(self, author):
        if self._last_updated is None:
            self._create()

        mins_ago = int((datetime.now() - self._last_updated).total_seconds() // 60)

        if mins_ago >= self._update_timer:
            mins_ago = 0
            self._create()

        lb = "```c++\n" + f"{self._title} [Updated: {mins_ago:,} min(s) ago]\n\n{self._leaderboard}" + "```"

        return lb[:2000]

    def _get_data(self):
        raise NotImplementedError()

    def _create(self):
        self._last_updated = datetime.now()

        widths = list(map(len, self._headers))

        rows = [self._headers.copy()]

        for rank, (member, member_data) in enumerate(self._get_data(), start=1):
            if rank > self._size:
                break

            username = member.display_name[:self._max_col_width]

            row = [f"#{rank:02d}", username]

            row.extend([str(getattr(member_data, col, None))[0:self._max_col_width] for col in self._columns])

            widths = [max(widths[i], len(col)) for i, col in enumerate(row)]

            rows.append(row)

        for row in rows:
            for i, col in enumerate(row[0:-1]):
                row[i] = f"{col}{'_' * (widths[i] - len(col))}"

        self._leaderboard = "\n".join(" ".join(row) for row in rows)


class ABOLeaderboard(LeaderboardBase):
    def __init__(self, guild, bot):
        super(ABOLeaderboard, self).__init__(
            title="Trophy Leaderboard",
            headers=["Lvl", "Trophies"],
            columns=["lvl", "trophies"],
            size=45
        )

        self.guild = guild
        self.bot = bot

    def _get_data(self):
        with DBConnection() as con:
            con.cur.execute(AboSQL.SELECT_ALL)
            all_data = con.cur.fetchall()

        all_data.sort(key=lambda u: u.trophies, reverse=True)

        svr = self.bot.svr_cache.get(self.guild.id, None)
        abo_role = (svr.roles if svr is not None else {}).get("member", None)

        role = self.guild.get_role(abo_role)

        for data in all_data:
            id_ = getattr(data, "userid", None)

            member = self.guild.get_member(id_)

            if member is None or member.bot or role not in member.roles:
                continue

            yield member, data


class CoinLeaderboard(LeaderboardBase):
    def __init__(self, guild, bot):
        super(CoinLeaderboard, self).__init__(
            title="Coin Leaderboard",
            headers=["Coins"],
            columns=["balance"],
            size=10
        )

        self.guild = guild
        self.bot = bot

    def _get_data(self):
        with DBConnection() as con:
            con.cur.execute(CoinsSQL.SELECT_ALL)
            all_data = con.cur.fetchall()

        all_data.sort(key=lambda u: u.balance, reverse=True)

        for data in all_data:
            id_ = getattr(data, "userid", None)

            member = self.guild.get_member(id_)

            if member is None or member.bot:
                continue

            yield member, data