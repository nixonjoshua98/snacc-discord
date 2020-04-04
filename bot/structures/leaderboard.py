import discord

from datetime import datetime
from bot.common.database import DBConnection


class Leaderboard:
    MAX_COL_WIDTH = 15

    def __init__(self, title: str, headers: list, col_attrs: list, **options):
        self._title = title
        self._headers = headers
        self._col_attrs = col_attrs

        self._size = options.get("size", 10)
        self._id_attr = options.get("id_attr", "userid")

        self._lb = None
        self._last_updated = None

    def get(self, author) -> str:
        if self._lb is None:
            self._create(author)

        return self._lb

    def get_data(self) -> list:
        raise NotImplementedError()

    def _create(self, author: discord.Member):
        rows = [["#", "Member"] + self._headers]
        col_widths = list(map(len, rows[0]))
        rank = 0

        for user_data in self.get_data():
            id_ = getattr(user_data, self._id_attr, None)
            member = author.guild.get_member(id_)

            if member is None or member.bot:
                continue

            rank += 1

            if rank > self._size:
                break

            entry = self._create_entry(rank, member, user_data)

            rows.append(entry)
            col_widths = [max(col_widths[i], len(col)) for i, col in enumerate(entry)]

        rows = self._add_padding(rows, col_widths)

        self._create_message(rows)

    def _create_entry(self, rank: int, member: discord.Member, user_data):
        username = member.display_name[:self.MAX_COL_WIDTH]

        row = [f"#{rank:02d}", username]

        for col in self._col_attrs:
            val = getattr(user_data, col, None)

            row.append(str(val)[0:self.MAX_COL_WIDTH])

        return row

    def _add_padding(self, rows: list, widths: list):
        for row in rows:
            for i, col in enumerate(row):
                row[i] = f"{col}{' ' * (widths[i] - len(col))}"

        return rows

    def _create_message(self, entries: list):
        self._lb = self._title + ("\n" * 2)

        for row in entries:
            self._lb += " ".join(row) + "\n"

        self._lb = "```c++\n" + self._lb + "```"

        self._last_updated = datetime.now()


class ABOLeaderboard(Leaderboard):
    def __init__(self):
        super(ABOLeaderboard, self).__init__(
            "Trophy Leaderboard",
            ["Lvl", "Trophies"], ["lvl", "trophies"],
            size=45
        )

    def get_data(self):
        with DBConnection() as con:
            con.cur.execute("SELECT userID, lvl, trophies FROM abo;")

            data = con.cur.fetchall()

        data.sort(key=lambda u: u.trophies, reverse=True)

        return data if data is not None else []


class CoinLeaderboard(Leaderboard):
    def __init__(self):
        super(CoinLeaderboard, self).__init__(
            "Coins Leaderboard",
            ["Coins"], ["balance"],
            size=10
        )

    def get_data(self):
        with DBConnection() as con:
            con.cur.execute("SELECT userID, balance FROM coins;")

            data = con.cur.fetchall()

        data.sort(key=lambda u: u.balance, reverse=True)

        return data if data is not None else []




