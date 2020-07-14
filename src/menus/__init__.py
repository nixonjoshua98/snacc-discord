
from .pagemenu import PageMenu
from .yesnomenu import YesNoMenu
from .textinput import TextInputDM, TextInputChannel


async def confirm(ctx, text: str) -> bool:
	menu = YesNoMenu(ctx.bot, text)

	await menu.send(ctx)

	return menu.get()


async def get_input(ctx, question, *, send_dm: bool):
	cls = TextInputDM if send_dm else TextInputChannel

	menu = cls(ctx.bot, ctx.author, question)

	await menu.send(ctx.author if send_dm else ctx)

	return menu.get()
