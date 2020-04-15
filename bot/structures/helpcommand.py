import discord
import asyncio

from discord.ext import commands

from bot.common.emoji import Emoji


class HelpCommand(commands.HelpCommand):
    def __init__(self):
        super(HelpCommand, self).__init__()

    async def get_pages(self):
        bot = self.context.bot

        all_commands = {}

        for cog, instance in bot.cogs.items():
            cmds = instance.get_commands()
            hidden = getattr(instance, "hidden", False)

            if not cmds or hidden:
                continue

            all_commands[instance] = cmds

        pages, max_pages = [],  len(all_commands)

        embed = discord.Embed(title=f"{bot.user.display_name}", color=0xff8000)
        embed.set_footer(text=bot.name, icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)

        pages.append(embed)

        for i, (cog, cmds) in enumerate(all_commands.items()):
            desc = f"{cog.qualified_name} Commands"

            embed = discord.Embed(title=f"{bot.user.display_name}", description=desc, color=0xff8000)

            embed.set_thumbnail(url=bot.user.avatar_url)

            for cmd in cmds:
                desc = getattr(cmd.callback, "__doc__", cmd.help)

                embed.add_field(name=f"[{'|'.join([cmd.name] + cmd.aliases)}] {cmd.usage or ''}", value=desc, inline=False)

            embed.set_footer(text=f"{bot.name} | Page {i + 1}/{max_pages}", icon_url=bot.user.avatar_url)

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
                react, _ = await bot.wait_for("reaction_add", timeout=30, check=wait_for)

            except asyncio.TimeoutError:
                await message.delete()
                break

            else:
                new_page = {
                    Emoji.ARROW_LEFT: max(0, current_page - 1),
                    Emoji.ARROW_RIGHT: min(current_page + 1, max_pages - 1)
                }.get(str(react.emoji), current_page)

                await react.remove(ctx.author)

                if new_page != current_page:
                    current_page = new_page
                    await message.edit(embed=pages[current_page])

