from datetime import datetime
from discord.ext import commands
from bot.common import DBConnection, AboSQL

from bot.common.queries import BankSQL, HangmanSQL


class LeaderboardBase:
    def __init__(self, title: str, headers: list, columns: list, **options):
        self._title = title
        self._headers = ["#", "Member"] + headers
        self._columns = columns

        self._size = options.get("size", 10)

        self._leaderboard = ""
        self._max_col_width = 15    # Max column width
        self._update_timer = 10
        self._last_updated = None

    async def get(self, author):
        if self._last_updated is None:
            await self._create()

        mins_ago = int((datetime.now() - self._last_updated).total_seconds() // 60)

        if mins_ago >= self._update_timer:
            mins_ago = 0
            await self._create()

        lb = "```c++\n" + f"{self._title}\n\n[Updated: {mins_ago:,} min(s) ago]\n\n{self._leaderboard}" + "```"

        return lb[:2000]

    def _get_data(self):
        raise NotImplementedError()

    async def _create(self):
        self._last_updated = datetime.now()

        widths = list(map(len, self._headers))

        rows = [self._headers.copy()]

        for rank, (member, member_data) in enumerate(await self._get_data(), start=1):
            if rank > self._size:
                break

            username = "Mysterious User"

            if member is not None:
                username = member.display_name[:self._max_col_width]

            row = [f"#{rank:02d}", username]

            row.extend([str(member_data.get(col, None))[0:self._max_col_width] for col in self._columns])

            widths = [max(widths[i], len(col)) for i, col in enumerate(row)]

            rows.append(row)

        for row in rows:
            for i, col in enumerate(row[0:-1]):
                row[i] = f"{col}{' ' * (widths[i] - len(col))}"

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

    async def _get_data(self):
        with DBConnection() as con:
            con.cur.execute(AboSQL.SELECT_ALL)
            all_data = con.cur.fetchall()

        all_data.sort(key=lambda u: u.trophies, reverse=True)

        role = await self.bot.get_cog("ABO").get_member_role(self.guild)

        ls = []

        for data in all_data:
            id_ = getattr(data, "userid", None)

            member = self.guild.get_member(id_)

            if member is None or member.bot or role not in member.roles:
                continue

            data = {"trophies": data.trophies, "lvl": data.lvl}

            ls.append(( member, data))

        return ls


class Leaderboard:
    def __init__(self, *, title: str, query: str, ctx: commands.Context, headers: list, columns: list):
        self.title = title
        self.ctx = ctx
        self.headers = ["#", "Player"] + headers
        self.columns = columns
        self.query = query

    async def create(self):
        ctx, bot = self.ctx, self.ctx.bot

        widths = list(map(len, self.headers))
        entries = [self.headers.copy()]

        for rank, row in enumerate(await bot.pool.fetch(self.query), start=1):
            user = ctx.guild.get_member(row["userid"])

            if user is None:
                user = bot.get_user(row["userid"])

            username = "Mysterious User" if user is None else user.display_name[0:20]

            entry = [f"#{rank:02d}", username]

            entry.extend([str(row.get(col, None))[0:20] for col in self.columns])

            widths = [max(widths[i], len(col)) for i, col in enumerate(entry)]

            entries.append(entry)

        for row in entries:
            for i, col in enumerate(row[0:-1]):
                row[i] = f"{col}{' ' * (widths[i] - len(col))}"

        return "```c++\n" + f"{self.title}\n\n" + "\n".join(" ".join(row) for row in entries) + "```"


class RichestPlayers(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(RichestPlayers, self).__init__(
            title="Richest Players",
            query=BankSQL.SELECT_RICHEST,
            ctx=ctx,
            headers=["Coins"],
            columns=["coins"]
        )


class HangmanWins(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(HangmanWins, self).__init__(
            title="Top Hangman Players",
            query=HangmanSQL.SELECT_BEST,
            ctx=ctx,
            headers=["Wins"],
            columns=["wins"]
        )

