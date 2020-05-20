import asyncio

import discord
from discord.ext import menus

from snacc.common.emoji import UEmoji


class EmbedMenu(menus.Menu):
    def __init__(self, pages: list):
        super(EmbedMenu, self).__init__(delete_message_after=True)

        self.current_page = 0

        self.pages = pages

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(embed=self.pages[0])

    @menus.button('\N{LEFTWARDS BLACK ARROW}')
    async def on_left_arrow(self, payload):
        if self.current_page > 0:
            self.current_page -= 1
            await self.message.edit(embed=self.pages[self.current_page])

    @menus.button('\N{BLACK RIGHTWARDS ARROW}')
    async def on_right_arrow(self, payload):
        if self.current_page + 1 < len(self.pages):
            self.current_page += 1
            await self.message.edit(embed=self.pages[self.current_page])


async def create(ctx, pages):
    bot = ctx.bot

    return await EmbedMenu(pages).start(ctx)

    def wait_for(react_, user):
        return user.id == ctx.author.id and react_.message.id == message.id

    current_page, max_pages = 0, len(pages)

    if max_pages == 1:
        return await ctx.send(embed=pages[current_page], delete_after=60)

    message = await ctx.send(embed=pages[current_page])

    for emoji in (UEmoji.ARROW_LEFT, UEmoji.ARROW_RIGHT):
        await message.add_reaction(emoji)

    while True:
        try:
            react, _ = await bot.wait_for("reaction_add", timeout=60, check=wait_for)

        except asyncio.TimeoutError:
            try:
                await message.delete()
            except discord.NotFound:
                pass

            break

        else:
            current_page = {
                UEmoji.ARROW_LEFT: max(0, current_page - 1),
                UEmoji.ARROW_RIGHT: min(current_page + 1, max_pages - 1)
            }.get(str(react.emoji), current_page)

            await react.remove(ctx.author)
            await message.edit(embed=pages[current_page])
