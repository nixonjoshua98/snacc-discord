from discord.ext import commands

from snacc.common.queries import ArenaStatsSQL, HangmanSQL


class Leaderboard:
    def __init__(self, *, title: str, query: str, size: int, ctx: commands.Context, headers: list, columns: list):
        self.title = title
        self.ctx = ctx
        self.headers = ["#", "User"] + headers
        self.columns = columns
        self.query = query
        self.size = size

    async def filter_results(self, results: list):
        return results

    def _create_row(self, rank, user, row):
        username = "Mysterious User" if user is None else user.display_name[0:20]

        entry = [f"#{rank:02d}", username]

        entry.extend([str(row.get(col, None))[0:20] for col in self.columns])

        return entry

    async def create(self, author):
        ctx, bot = self.ctx, self.ctx.bot

        widths = list(map(len, self.headers))
        entries = [self.headers.copy()]

        author_row = None

        results = await self.filter_results(await bot.pool.fetch(self.query))

        for rank, row in enumerate(results, start=1):
            id_ = row["user_id"]

            if rank > self.size and author_row is not None:
                break

            user = ctx.guild.get_member(id_)

            if user is None:
                user = bot.get_user(id_)

            if rank <= self.size or author_row is None:
                entry = self._create_row(rank, user, row)

                if id_ == author.id and author_row is None:
                    author_row = self._create_row(rank, user, row)

                if rank <= self.size:
                    widths = [max(widths[i], len(col)) for i, col in enumerate(entry)]

                    entries.append(entry)

        for i, row in enumerate(entries):
            for j, col in enumerate(row[0:-1]):
                row[j] = f"{col}{' ' * (widths[j] - len(col))}"

        text = self.title + "\n\n" + "\n".join(" ".join(row) for row in entries) + "\n"

        if author_row is not None:
            text += "-" * sum(widths) + "\n"
            text += " ".join(f"{col}{' ' * (widths[j] - len(col))}" for j, col in enumerate(author_row))

        return "```c++\n" + text + "```"


class TrophyLeaderboard(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(TrophyLeaderboard, self).__init__(
            title="Trophy Leaderboard",
            query=ArenaStatsSQL.SELECT_TROPHY_LEADERBOARD,
            size=10,
            ctx=ctx,
            headers=["Level", "Trophies"],
            columns=["level", "trophies"],
        )

    async def filter_results(self, results: list):
        svr_config = await self.ctx.bot.get_server(self.ctx.guild)

        role = self.ctx.guild.get_role(svr_config["member_role"])

        ls = []

        member_table = {member.id: member for member in role.members}

        for row in results:
            member = member_table.get(row["user_id"])

            if member is not None:
                ls.append(row)

        return ls


class HangmanLeaderboard(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(HangmanLeaderboard, self).__init__(
            title="Top Hangman Players",
            query=HangmanSQL.SELECT_BEST,
            size=10,
            ctx=ctx,
            headers=["Wins"],
            columns=["wins"]
        )