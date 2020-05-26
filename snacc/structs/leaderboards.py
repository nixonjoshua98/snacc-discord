from snacc.common.queries import ArenaStatsSQL, HangmanSQL

from snacc.structs.menus import Menu


def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


class TextLeaderboardBase:
    def __init__(self, *, title: str, query: str, columns: list, order_col: str, **options):
        headers = options.get("headers", [ele.title() for ele in columns])

        self.title = title
        self.columns = columns
        self.query = query
        self.order_col = order_col

        self.headers = ["#", "User"] + headers

        self.max_rows = options.get("max_rows", None)
        self.page_size = options.get("page_size", 15)

    async def send(self, ctx):
        import time

        now = time.time()

        pages = await self._create_pages(ctx)

        print(f"{self.title}: {round(time.time() - now, 3)}s")

        await Menu(pages, timeout=60, delete_after=False).send(ctx)

    async def filter_results(self, ctx, results: list):
        return results

    async def execute_query(self, ctx) -> list:
        return await ctx.bot.pool.fetch(self.query)

    async def _create_pages(self, ctx):
        headers, entries, author_entry = await self._create(ctx)

        pages = []

        chunks = tuple(chunk_list(entries, self.page_size))

        for i, chunk in enumerate(chunks, start=1):
            message = "Trophy Leaderboard" + ("\n" * 2)

            message += headers + "\n"

            row = "\n".join(map(lambda ele: "".join(ele), chunk))

            message += row

            if author_entry is not None:
                message += "\n" + "-" * (len(row) // len(chunk))
                message += "\n" + author_entry

            pages.append(f"```c++\n{message}```")

        return pages

    async def _create(self, ctx) -> tuple:
        bot, author = ctx.bot, ctx.author

        widths = list(map(len, self.headers))
        entries = []

        author_row, prev_val, rank = None, None, 0

        results = await self.execute_query(ctx)
        results = await self.filter_results(ctx, results)

        for row in results:
            rank = (rank + 1) if prev_val is None or row[self.order_col] < prev_val else rank

            prev_val = row[self.order_col]

            num_entries = len(entries) - 1

            # We have everything we need so just end the loop
            if (self.max_rows is not None and num_entries >= self.max_rows) and author_row is not None:
                break

            # Get some reference to a user (can be None)
            user = self._get_user(ctx, row["user_id"])

            # Create the text row for the user
            entry = self._create_row(rank, user, row)

            author_row = entry if row["user_id"] == author.id else author_row

            if self.max_rows is None or num_entries < self.max_rows:
                widths = [max(widths[i], len(col)) for i, col in enumerate(entry)]

                entries.append(entry)

        rows = [self._pad_row(row, widths) for row in entries]

        headers = self._pad_row(self.headers, widths)

        if author_row is not None:
            author_row = self._pad_row(author_row, widths)

        return headers, rows, author_row

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

    def _pad_row(self, row, widths):
        return " ".join(f"{col}{' ' * (widths[j] - len(col))}" for j, col in enumerate(row))


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


class HangmanLeaderboard(TextLeaderboardBase):
    def __init__(self):
        super(HangmanLeaderboard, self).__init__(
            title="Top Hangman Players",
            query=HangmanSQL.SELECT_HANGMAN_LEADERBOARD,
            columns=["wins"],
            order_col="wins"
        )
