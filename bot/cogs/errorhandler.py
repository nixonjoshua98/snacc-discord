import datetime

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

        elif isinstance(esc, commands.MissingRequiredArgument):
            arg = esc.args[0].split(" ")[0]

            await ctx.send(f"`{arg}` is a required argument that is missing.")

        elif isinstance(esc, commands.CommandOnCooldown):
            seconds = float(esc.args[0].split(" ")[-1][0:-1])

            cd = datetime.timedelta(seconds=int(seconds))

            await ctx.send(f"You are on cooldown. Try again in {cd}")

        else:
            await ctx.send(f":x: Unhandled exception: {esc}")


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
