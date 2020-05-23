from snacc.common.queries import ArenaStatsSQL, HangmanSQL


class TextLeaderboardBase:
    def __init__(self, *, title: str, query: str, size: int, headers: list, columns: list, order_col: str):
        self.title = title
        self.headers = ["#", "User"] + headers
        self.columns = columns
        self.query = query
        self.size = size
        self.order_col = order_col

    async def send(self, ctx):
        await ctx.send(await self._create(ctx))

    async def filter_results(self, ctx, results: list):
        return results

    async def execute_query(self, ctx) -> list:
        return await ctx.bot.pool.fetch(self.query)

    def _create_row(self, rank, user, row):
        username = "Unknown User" if user is None else user.display_name[0:20]

        entry = [f"#{rank:02d}", username]

        entry.extend([str(row.get(col, None))[0:20] for col in self.columns])

        return entry

    def _get_user(self, ctx, id_):
        user = ctx.guild.get_member(id_)

        if user is None:
            user = ctx.bot.get_user(id_)

        return user

    def _create_author_section(self, widths, row):
        """ Leaderboard footer. """

        text = "-" * (sum(widths) + 1) + "\n"
        text += " ".join(f"{col}{' ' * (widths[j] - len(col))}" for j, col in enumerate(row))

        return text

    def _create_spaced_rows(self, widths, rows):
        """ Pad the rows so each row is uniformally spaced. """

        text_rows = []

        for i, row in enumerate(rows):
            text_rows.append([])

            for j, col in enumerate(row):
                text_rows[-1].append(f"{col}{' ' * (widths[j] - len(col))}")

        return text_rows

    async def _create(self, ctx):
        bot, author = ctx.bot, ctx.author

        widths = list(map(len, self.headers))
        entries = [self.headers.copy()]

        author_row, prev_val, rank = None, None, 0

        results = await self.execute_query(ctx)
        results = await self.filter_results(ctx, results)

        for row in results:
            rank = (rank + 1) if prev_val is None or row[self.order_col] < prev_val else rank

            prev_val = row[self.order_col]

            num_entries = len(entries) - 1

            # We have everything we need so just end the loop
            if num_entries >= self.size and author_row is not None:
                break

            # Get some reference to a user (can be None)
            user = self._get_user(ctx,  row["user_id"])

            # Create the text row for the user
            entry = self._create_row(rank, user, row)

            if row["user_id"] == author.id:
                author_row = entry

            if num_entries < self.size:
                widths = [max(widths[i], len(col)) for i, col in enumerate(entry)]

                entries.append(entry)

        text_rows = self._create_spaced_rows(widths, entries)

        text = self.title + "\n\n" + "\n".join(" ".join(row) for row in text_rows) + "\n"

        if author_row is not None:
            text += self._create_author_section(widths, author_row)

        return "```c++\n" + text + "```"


class TrophyLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(TrophyLeaderboard, self).__init__(
            title="Trophy Leaderboard",
            query=ArenaStatsSQL.SELECT_LEADERBOARD,
            size=45,
            headers=["Level", "Trophies"],
            columns=["level", "trophies"],
            order_col="trophies"
        )

    async def execute_query(self, ctx) -> list:
        svr_config = await ctx.bot.get_server(ctx.guild)

        role = ctx.guild.get_role(svr_config["member_role"])

        results = await ctx.bot.pool.fetch(self.query, tuple(member.id for member in role.members))

        return results


class HangmanLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(HangmanLeaderboard, self).__init__(
            title="Top Hangman Players",
            query=HangmanSQL.SELECT_HANGMAN_LEADERBOARD,
            size=10,
            headers=["Wins"],
            columns=["wins"],
            order_col="wins"
        )
