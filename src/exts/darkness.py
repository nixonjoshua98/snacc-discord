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
    @commands.cooldown(1, 60 * 60 * 12, commands.BucketType.member)
    @commands.max_concurrency(1, commands.BucketType.member)
    async def application(self, ctx):
        """ Apply to the guild! """

        await ctx.send("Check your DM.")

        questions = {
            "username": (inputs.get_input, Arguments(ctx, "What is your in-game-name?", send_dm=True)),

            "trophies": (inputs.options, Arguments(ctx,
                                                   "What is your trophy count?",
                                                   ("0-3000", "3001-4000", "4001-5000", "5001-6000", "6000+"),
                                                   send_dm=True
                                                   )
                         ),

            "play time": (inputs.options, Arguments(ctx,
                                                    "How long have you been playing?",
                                                    ("0-3 months", "4-7 months", "8+ months"),
                                                    send_dm=True
                                                    )
                          ),

            "device": (inputs.options, Arguments(ctx,
                                                 "How do you play?",
                                                 ("Phone/Tablet", "Emulator", "Spare phone", "Other"),
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

        today = datetime.utcnow().strftime('%d/%m/%Y %X')

        embed.set_footer(text=f"{str(ctx.author)} | UTC: {today}", icon_url=ctx.author.avatar_url)

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Darkness())
