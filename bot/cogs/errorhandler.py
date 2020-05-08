from bot.common import errors

from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.on_command_error = self.on_command_error

    async def on_command_error(self, ctx, esc):
        if isinstance(esc, commands.CommandNotFound):
            return None

        elif isinstance(esc, errors.InvalidCoinSide):
            await ctx.send("That is not a valid coin side.")

        elif isinstance(esc, errors.NotEnoughMoney):
            await ctx.send("You do not have enough money .")

        elif isinstance(esc, errors.MemberRoleNotFound):
            await ctx.send("A server member role needs to be set first.")

        elif isinstance(esc, errors.InvalidRoleTag):
            await ctx.send(f"Invalid Tag. Tags include: **{', '.join(esc.tags)}**")

        else:
            await ctx.send(f":x: Unhandled exception: {esc}")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
