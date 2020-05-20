import asyncio

import discord

from snacc.common.emoji import UEmoji


async def create(ctx, pages):
    bot = ctx.bot

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
