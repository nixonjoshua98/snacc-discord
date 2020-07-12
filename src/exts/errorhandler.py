import datetime

from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.bot.on_command_error = self.on_command_error

    async def on_command_error(self, ctx, esc):
        if isinstance(esc, commands.CommandNotFound):
            return None

        elif isinstance(esc, commands.CommandOnCooldown):
            seconds = float(esc.args[0].split(" ")[-1][0:-1])

            cd = datetime.timedelta(seconds=int(seconds))

            await ctx.send(f"You are on cooldown. Try again in `{cd}`")

        elif isinstance(esc, commands.MissingRequiredArgument):
            arg = esc.args[0].split(" ")[0]

            await ctx.send(f"`{arg}` is a required argument that is missing.")

        elif isinstance(esc, commands.CheckFailure):
            await ctx.send("You do not have access to this command.")

        elif isinstance(esc, commands.MaxConcurrencyReached):
            await ctx.send("You are doing that too fast.")

        elif isinstance(esc, commands.CommandError):
            await ctx.send(esc)

        else:
            print(esc)

            await ctx.send(esc)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
