import discord
import asyncio

from discord.ext import commands

import itertools

from bot.common.emoji import Emoji


class HelpCommand(commands.HelpCommand):
    async def create_help_first_page(self, num_pages: int = None):
        bot = self.context.bot

        embed = discord.Embed(title=f"**{bot.user.display_name} Help**")

        footer = bot.name

        if num_pages is not None:
            footer = f"{bot.name} | Page 1/{num_pages}"

        embed.set_footer(text=footer, icon_url=bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)

        return embed

    async def create_help_page(self, category, cmds, page: int, num_pages: int) -> discord.Embed:
        bot = self.context.bot

        embed = discord.Embed(title=f"**{bot.user.display_name} Help**", description=f"{category} Commands")

        for cmd in cmds:
            embed.add_field(name=f"[{cmd}] {cmd.usage}", value=f"{cmd.help}", inline=False)

        embed.set_footer(text=f"{bot.name} | Page {page}/{num_pages}", icon_url=bot.user.avatar_url)

        return embed

    async def send_bot_help(self, mapping):
        ctx: commands.Context = self.context
        bot = ctx.bot

        def wait_for(react, user):
            return (
                    user.id == ctx.author.id and  # Listen to the author only
                    react.message.id == message.id and  # Help message only
                    str(react.emoji) in (Emoji.ARROW_RIGHT, Emoji.ARROW_LEFT)  # Arrows
            )

        def get_category(command):
            return command.cog.qualified_name if command.cog is not None else "no_category"

        # Group commands by their Cog and remove commands without a Cog
        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)
        grouped = [(cat, (list(cmds))) for cat, cmds in itertools.groupby(filtered, key=get_category)]
        grouped = list(filter(lambda ls: ls[0] != "no_category", grouped))

        shown_help_page = 0  # Current page which is being shown
        num_pages = len(grouped) + 1  # +1 for the first help page

        first_page = await self.create_help_first_page(num_pages)

        pages = [first_page]

        message = await ctx.send(embed=first_page)

        # Add navigation buttons
        for emoji in (Emoji.ARROW_LEFT, Emoji.ARROW_RIGHT):
            await message.add_reaction(emoji)

        # Create the pages
        for i, (category, cmds) in enumerate(grouped, start=1):
            embed = await self.create_help_page(category, cmds, i + 1, num_pages)

            pages.append(embed)

        while True:
            try:
                # Wait for a reaction
                react, _ = await bot.wait_for("reaction_add", timeout=30, check=wait_for)

            except asyncio.TimeoutError:
                await message.delete()
                break

            else:
                shown_help_page = {
                    Emoji.ARROW_LEFT: max(0, shown_help_page - 1),
                    Emoji.ARROW_RIGHT: min(shown_help_page + 1, len(pages) - 1)
                }.get(str(react.emoji), shown_help_page)

                await react.remove(ctx.author)

            await message.edit(embed=pages[shown_help_page])

