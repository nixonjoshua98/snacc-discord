import discord

from src.structs.displaypages import DisplayPages
from src.structs.textpage import TextPage


def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


class TextLeaderboard:
    def __init__(self, *, title: str, columns: list, query_func, order_by: str, **options):
        self.title = title
        self.columns = columns
        self.order_col = order_by

        self.query_func = query_func

        self.headers = ["#", "User"] + options.get("headers", [ele.title() for ele in columns])

        self.max_rows = options.get("max_rows", 15)
        self.page_size = 15

    async def send(self, ctx):
        pages = await self._create_pages(ctx)

        if pages:
            if len(pages) == 1:
                return await ctx.send(pages[0])

            await DisplayPages(pages, timeout=180.0).send(ctx)

        else:
            await ctx.send("No records yet.")

    async def _create_pages(self, ctx):
        entries, author_entry = await self._get_data(ctx)

        pages = []

        chunks = tuple(chunk_list(entries, self.page_size))

        for i, chunk in enumerate(chunks, start=1):
            title = self.title + (f" [Page {i} / {len(chunks)}]" if len(chunks) > 1 else "")

            page = TextPage(title=title, headers=self.headers)

            for row in chunk:
                page.add(row)

            if author_entry is not None:
                page.set_footer(author_entry)

            pages.append(page)

        return tuple(map(lambda ele: ele.get(), pages))

    async def _filter_results(self, ctx, results):
        prev_row, rank = None, 0

        for row in results:
            user = row.get("user", row.get("_id"))

            user = ctx.guild.get_member(user) or ctx.bot.get_user(user)

            if user is None:
                continue

            if prev_row is None or prev_row.get(self.order_col, 0) > row.get(self.order_col, 0):
                prev_row, rank = row, rank + 1

            yield rank, user, row

    async def _get_data(self, ctx) -> tuple:
        entries = []

        author_row = None

        results = await self.query_func()

        async for rank, user, row in self._filter_results(ctx, results):

            num_entries = len(entries)

            if (self.max_rows is not None and num_entries >= self.max_rows) and author_row is not None:
                break

            entry = self._create_row(rank, user, row)

            author_row = entry if getattr(user, "id", None) == ctx.author.id else author_row

            if self.max_rows is None or num_entries < self.max_rows:
                entries.append(entry)

        return entries, author_row

    def _create_row(self, rank, user, row):
        username = str(user) if isinstance(user, (discord.User, str, int)) else user.display_name

        entry = [f"#{rank:02d}", username]

        entry.extend([str(row.get(col, '')) for col in self.columns])

        return entry
