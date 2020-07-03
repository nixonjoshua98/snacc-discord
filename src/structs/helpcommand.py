import discord
from discord.ext import commands

from datetime import datetime

from src.menus.pagemenu import PageMenu


def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]


class HelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super(HelpCommand, self).__init__()

    async def create_start_page(self):
        bot, ctx = self.context.bot, self.context

        embed = discord.Embed(title=f"{bot.user.display_name}", color=0xff8000)
        today = datetime.utcnow().strftime('%d/%m/%Y %X')

        embed.set_footer(text=f"{ctx.bot.user.name} | {today}", icon_url=ctx.bot.user.avatar_url)
        embed.set_thumbnail(url=bot.user.avatar_url)

        return embed

    async def get_pages(self):
        bot, ctx = self.context.bot, self.context

        all_commands = {}
        descriptions = []

        for cog, instance in bot.cogs.items():
            cmds = await self.filter_commands(instance.get_commands())
            cmds = tuple(chunk_list(cmds, 10))

            for i, j in enumerate(cmds):
                descriptions.append(instance.__doc__ or "")

                all_commands[f"**{cog} | Page ({i + 1}/{len(cmds)})**"] = j

        pages, max_pages = [],  len(all_commands)

        home_page = await self.create_start_page()

        pages.append(home_page)

        for i, (cog, cmds) in enumerate(all_commands.items()):
            embed = discord.Embed(title=cog, description=descriptions[i], color=0xff8000)

            embed.set_thumbnail(url=bot.user.avatar_url)
            embed.set_footer(text=f"{bot.user.name} | Page {i + 1}/{max_pages}", icon_url=bot.user.avatar_url)

            for cmd in cmds:
                sig = cmd.usage or cmd.signature.replace("[", "<").replace("]", ">")
                val = str(cmd.callback.__doc__)

                name = f"[{'|'.join([cmd.name] + cmd.aliases)}] {sig}"

                embed.add_field(name=name, value=val, inline=False)

            pages.append(embed)

        return pages

    async def send_bot_help(self, mapping):
        pages = await self.get_pages()

        await PageMenu(self.context.bot, pages, timeout=60.0).send(self.context)
