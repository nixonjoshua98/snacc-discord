import discord
import asyncio

from discord.ext import commands

from bot.common.emoji import Emoji


def chunks(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i : i + n]


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super(HelpCommand, self).__init__()

    async def get_pages(self):
        bot, ctx = self.context.bot, self.context

        all_commands = {}

        for cog, instance in bot.cogs.items():
            if getattr(instance, "hidden", False):
                continue

            cmds = await self.filter_commands(instance.get_commands())
            cmds = tuple(chunks(cmds, 10))

            for i, j in enumerate(cmds):
                all_commands[f"{cog} | Page ({i + 1}/{len(cmds)})"] = j

        pages, max_pages = [],  len(all_commands)

        embed = discord.Embed(title=f"{bot.user.display_name}", color=0xff8000)

        embed.set_footer(text=bot.user.display_name, icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)

        pages.append(embed)

        for i, (cog, cmds) in enumerate(all_commands.items()):
            embed = discord.Embed(title=f"{bot.user.display_name}", description=cog, color=0xff8000)

            embed.set_thumbnail(url=bot.user.avatar_url)

            for cmd in cmds:
                name = f"[{'|'.join([cmd.name] + cmd.aliases)}] {cmd.usage or ''}"
                value = getattr(cmd.callback, "__doc__", cmd.help)

                embed.add_field(name=name, value=value, inline=False)

            embed.set_footer(text=f"{bot.user.name} | Page {i + 1}/{max_pages}", icon_url=bot.user.avatar_url)

            pages.append(embed)

        return pages

    async def send_bot_help(self, mapping):
        ctx: commands.Context = self.context
        bot = ctx.bot

        def wait_for(react, user):
            return (
                    user.id == ctx.author.id and  # Listen to the author only
                    react.message.id == message.id and  # Help message only
                    str(react.emoji) in (Emoji.ARROW_RIGHT, Emoji.ARROW_LEFT)  # Arrows
            )

        pages = await self.get_pages()

        current_page, max_pages = 0, len(pages)

        message = await ctx.send(embed=pages[current_page])

        # Add navigation buttons
        for emoji in (Emoji.ARROW_LEFT, Emoji.ARROW_RIGHT):
            await message.add_reaction(emoji)

        while True:
            try:
                # Wait for a reaction
                react, _ = await bot.wait_for("reaction_add", timeout=60, check=wait_for)

            except asyncio.TimeoutError:
                try:
                    await message.delete()
                except discord.NotFound as e:
                    pass

                break

            else:
                # Update which page the user is currently viewing
                new_page = {
                    Emoji.ARROW_LEFT: max(0, current_page - 1),
                    Emoji.ARROW_RIGHT: min(current_page + 1, max_pages - 1)
                }.get(str(react.emoji), current_page)

                await react.remove(ctx.author)

                if new_page != current_page:
                    current_page = new_page
                    await message.edit(embed=pages[current_page])

