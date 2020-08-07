import discord

from discord.ext import commands

from datetime import datetime

from src import inputs
from src.common import MainServer, checks


class Arguments:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class Darkness(commands.Cog):

    @checks.main_server_only()
    @commands.command(name="join")
    @commands.cooldown(1, 60 * 60 * 12, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.user)
    async def application(self, ctx):
        """ Apply to the guild! """

        await ctx.send("I have DM'ed you")

        embed = discord.Embed(title="Guild Application", colour=discord.Color.orange())

        for q in (
                "What is your in-game-name?",
                "What is your trophy count?",
                "How long have you been playing?",
                "How do you play?",
                "How long do you play the game each day?"
        ):
            resp = await inputs.get_input(ctx, q, send_dm=True)

            if resp is None:
                return self.application.reset_cooldown(ctx)

            embed.add_field(name=q, value=resp, inline=False)

        channel = ctx.bot.get_channel(MainServer.APP_CHANNEL)

        embed.timestamp = datetime.utcnow()

        embed.set_footer(text=f"{str(ctx.author)}", icon_url=ctx.author.avatar_url)

        await ctx.send("Your application is done!")

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Darkness())
