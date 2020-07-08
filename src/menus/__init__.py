
from .pagemenu import PageMenu
from .yesnomenu import YesNoMenu


async def confirm(ctx, text: str) -> bool:
	menu = YesNoMenu(ctx.bot, text)

	await menu.send(ctx)

	return menu.get()