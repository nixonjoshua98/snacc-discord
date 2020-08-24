
async def send_pages(ctx, pages, *, send_dm: bool = False):
	from .pages import Pages

	await Pages(ctx.bot, ctx.author, pages).send(ctx.author if send_dm else ctx.channel)


async def show_leaderboard(ctx, title, columns, order_by, query_func, **kwargs):
	from .textleaderboard import TextLeaderboard

	await TextLeaderboard(title=title, columns=columns, order_by=order_by, query_func=query_func, **kwargs).send(ctx)
