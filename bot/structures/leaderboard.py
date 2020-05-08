from discord.ext import commands

from bot.common.queries import AboSQL, BankSQL, HangmanSQL


class Leaderboard:
    def __init__(self, *, title: str, query: str, ctx: commands.Context, headers: list, columns: list):
        self.title = title
        self.ctx = ctx
        self.headers = ["#", "Player"] + headers
        self.columns = columns
        self.query = query

    async def filter_results(self, results: list):
        return results

    async def create(self):
        ctx, bot = self.ctx, self.ctx.bot

        widths = list(map(len, self.headers))
        entries = [self.headers.copy()]

        results = await self.filter_results(await bot.pool.fetch(self.query))

        for rank, row in enumerate(results, start=1):
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


class MoneyLeaderboard(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(MoneyLeaderboard, self).__init__(
            title="Richest Players",
            query=BankSQL.SELECT_RICHEST,
            ctx=ctx,
            headers=["Money"],
            columns=["money"]
        )


class HangmanLeaderboard(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(HangmanLeaderboard, self).__init__(
            title="Top Hangman Players",
            query=HangmanSQL.SELECT_BEST,
            ctx=ctx,
            headers=["Wins"],
            columns=["wins"]
        )


class TrophyLeaderboard(Leaderboard):
    def __init__(self, ctx: commands.Context):
        super(TrophyLeaderboard, self).__init__(
            title="Trophy Leaderboard",
            query=AboSQL.SELECT_BEST,
            ctx=ctx,
            headers=["Lvl", "Trophies"],
            columns=["lvl", "trophies"]
        )

    async def filter_results(self, results: list):
        ctx, bot = self.ctx, self.ctx.bot

        svr_config = await bot.get_server(ctx.guild)

        role = ctx.guild.get_role(svr_config["memberrole"])

        ls = []

        member_table = {member.id: member for member in role.members}

        for row in results:
            member = member_table.get(row["userid"])

            if member is not None:
                ls.append(row)

        return ls
