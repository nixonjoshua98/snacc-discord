
async def send_pages(ctx, pages, *, send_dm: bool = False):
	from .pages import Pages

	await Pages(ctx.bot, ctx.author, pages).send(ctx.author if send_dm else ctx.channel)


async def confirm(ctx, question, *, send_dm: bool = False):
	from .confirmation import Confirmation

	menu = Confirmation(ctx.bot, ctx.author, question)

	await menu.send(ctx.author if send_dm else ctx.channel)

	return menu.get()


async def get_input(ctx, question, *, send_dm: bool = False):
	from .textinput import TextInputChannel, TextInputDM

	cls = TextInputDM if send_dm else TextInputChannel

	menu = cls(ctx.bot, ctx.author, question)

	await menu.send(ctx.author if send_dm else ctx.channel)

	return menu.get()


async def options(ctx, title, ops, *, send_dm: bool = False):
	from .optionmenu import OptionMenu

	menu = OptionMenu(ctx.bot, ctx.author, title, ops)

	await menu.send(ctx.author if send_dm else ctx.channel)

	return menu.get()


async def show_leaderboard(ctx, title, columns, order_by, query_func):
	from .textleaderboard import TextLeaderboard

	await TextLeaderboard(title=title, columns=columns, order_by=order_by, query_func=query_func).send(ctx)
