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

        questions = {
            "username": (inputs.get_input, Arguments(ctx, "What is your in-game-name?", send_dm=True)),

            "trophies": (inputs.get_input, Arguments(
                ctx,
                "What is your trophy count?",
                send_dm=True,
                validation=lambda s: s.isdigit()
            )
                         ),

            "play time": (inputs.options, Arguments(ctx,
                                                    "How long have you been playing?",
                                                    ("0-1 months", "2-4 months", "5-6 months", "6+ months"),
                                                    send_dm=True
                                                    )
                          ),

            "device": (inputs.options, Arguments(ctx,
                                                 "How do you play?",
                                                 ("Phone/Tablet", "PC/Laptop", "Other"),
                                                 send_dm=True
                                                 )
                       ),
            "daily playtime": (inputs.options, Arguments(ctx,
                                                         "How many hours do you play daily?",
                                                         (
                                                             "0-6 hours",
                                                             "7-12 hours",
                                                             "13-18 hours",
                                                             "19-24 hours",
                                                         ),
                                                         send_dm=True
                                                         )
                               ),
        }

        answers = dict()

        # - - - ASK QUESTIONS - - - #

        for k in questions:
            func, args = questions[k]

            response = await func(*args.args, **args.kwargs)

            if response is None:
                return self.application.reset_cooldown(ctx)

            answers[k] = response

        await ctx.author.send("Your application is complete!")

        #  - - - LOG RESULTS - - - #

        channel = ctx.bot.get_channel(MainServer.APP_CHANNEL)

        embed = discord.Embed(title="Guild Application", colour=discord.Color.orange())

        for k, v in answers.items():
            embed.add_field(name=k.title(), value=v, inline=False)

        embed.timestamp = datetime.utcnow()

        embed.set_footer(text=f"{str(ctx.author)}", icon_url=ctx.author.avatar_url)

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Darkness())