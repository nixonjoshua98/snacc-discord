import discord

from discord.ext import commands

from datetime import datetime

from src import inputs
from src.common import MainServer, checks


class Arguments:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class GuildApplications(commands.Cog, name="Guild Applications"):

    @checks.main_server_only()
    @commands.command(name="application", aliases=["app", "join"])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def application(self, ctx):
        """ Apply to the guild! """

        if not await inputs.confirm(ctx, "Are you looking to join the Darkness Alliance?"):
            return

        await ctx.send("Check your DM. I have started an application with you.")

        questions = {
            "trophies": (inputs.options,
                         Arguments(ctx,
                                   "What is your trophy count?",
                                   ("0-1000", "1001-2500", "2501-4000", "4001-5000", "5000+"),
                                   send_dm=True)
                         ),

            "play time": (inputs.options,
                          Arguments(ctx,
                                    "How long have you played?",
                                    ("0-2 months", "3-5 months", "6-8 months", "9+ months"),
                                    send_dm=True)
                          ),

            "device": (inputs.options,
                       Arguments(ctx,
                                 "How do you play?",
                                 ("Phone/Tablet", "PC", "Spare Phone", "Other"),
                                 send_dm=True)
                       ),
        }

        answers = dict()
        current_question = 0
        keys = tuple(questions.keys())

        # - - - ASK QUESTIONS - - - #

        while current_question < len(keys):
            question_template = questions[keys[current_question]]

            func, args = question_template

            response = await func(*args.args, **args.kwargs)

            # Timed out
            if response is None:
                return

            answers[keys[current_question]] = response

            current_question += 1

        await ctx.author.send("Your application has been completed!")

        #  - - - LOG RESULTS - - - #

        channel = ctx.bot.get_channel(MainServer.APP_CHANNEL)

        embed = discord.Embed(title="Guild Application", colour=discord.Color.orange())

        for k, v in answers.items():
            embed.add_field(name=k.title(), value=v, inline=False)

        today = datetime.utcnow().strftime('%d/%m/%Y %X')

        embed.set_footer(text=f"{str(ctx.author)} | UTC: {today}", icon_url=ctx.author.avatar_url)

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(GuildApplications())
