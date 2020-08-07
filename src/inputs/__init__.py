
async def send_pages(ctx, pages, *, send_dm: bool = False):
	from .pages import Pages

	await Pages(ctx.bot, ctx.author, pages).send(ctx.author if send_dm else ctx.channel)


async def get_input(ctx, question, *, send_dm: bool = False, validation=None):
	from .textinput import TextInputChannel, TextInputDM

	cls = TextInputDM if send_dm else TextInputChannel

	menu = cls(ctx.bot, ctx.author, question, validation=validation)

	await menu.send(ctx.author if send_dm else ctx.channel)

	return menu.get()


async def show_leaderboard(ctx, title, columns, order_by, query_func, **kwargs):
	from .textleaderboard import TextLeaderboard

	await TextLeaderboard(title=title, columns=columns, order_by=order_by, query_func=query_func, **kwargs).send(ctx)


async def options(ctx, title, ops, *, send_dm: bool = False):
	from .optionmenu import OptionMenu

	menu = OptionMenu(ctx.bot, ctx.author, title, ops)

	await menu.send(ctx.author if send_dm else ctx.channel)

	return menu.get()
