import discord

import datetime as dt

from discord.ext import commands

from discord.ext.commands import (
    CommandNotFound,
    CommandOnCooldown,
    MissingRequiredArgument,
    MissingRole,
    MaxConcurrencyReached
)

from src.common.errors import (
    GlobalCheckFail
)


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.on_command_error = self.on_command_error

    async def on_command_error(self, ctx, esc):
        if isinstance(esc, CommandNotFound):
            return None

        elif isinstance(esc, GlobalCheckFail):
            print(esc)

        elif isinstance(esc, MaxConcurrencyReached):
            await ctx.send(f"{str(ctx.author)}, slow down")

        elif isinstance(esc, CommandOnCooldown):
            seconds = float(esc.args[0].split(" ")[-1][0:-1])

            cd = dt.timedelta(seconds=int(seconds))

            await ctx.send(f"You are on cooldown. Try again in `{cd}`")

        elif isinstance(esc, MissingRequiredArgument):
            arg = esc.args[0].split(" ")[0]

            await ctx.send(f"`{arg}` is a required argument that is missing.")

        elif isinstance(esc, MissingRole):
            await ctx.send(f"Role `{esc.missing_role}` is required to run this command.")

        else:
            await ctx.send(esc)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
