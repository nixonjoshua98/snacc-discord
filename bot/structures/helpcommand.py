import discord

from discord.ext import commands

import itertools


class HelpCommand(commands.DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        ctx, bot = self.context, self.context.bot

        embed: discord.Embed = bot.create_embed(title=f"**{ctx.bot.user.display_name} Commands**")

        if bot.description:
            embed.description = bot.description

        def get_category(command):
            return command.cog.qualified_name if command.cog is not None else "no_category"

        filtered = await self.filter_commands(bot.commands, sort=True, key=get_category)

        for category, cmds in itertools.groupby(filtered, key=get_category):
            if category is not "no_category":
                cmds = sorted(cmds, key=lambda c: c.name)

                text = lambda c: f"`{ctx.prefix}{c.name}" \
                                 f"{f' {c.usage}' if c.usage is not None else ''}" \
                                 f"{f' ({c.help})' if c.help is not None else ''}`"

                value = "\n".join(map(text, cmds))

                embed.add_field(name=category, value=value)

        return await ctx.send(embed=embed)
