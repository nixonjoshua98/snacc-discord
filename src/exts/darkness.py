import discord

from discord.ext import commands

from datetime import datetime

from src import inputs
from src.common import MainServer, checks


class Darkness(commands.Cog):

    @checks.main_server_only()
    @commands.command(name="join")
    @commands.max_concurrency(1, commands.BucketType.user)
    async def application(self, ctx):
        """ Apply to the guild! """

        await ctx.send("Check your DM.")

        questions = {
            "trophies": inputs.options(ctx,
                                       "What is your trophy count?",
                                       ("0-1000", "1001-2500", "2501-4000", "4001-5000", "5000+"),
                                       send_dm=True
                                       ),

            "play time": inputs.options(ctx,
                                        "How long have you played?",
                                        ("0-2 months", "3-5 months", "6-8 months", "9+ months"),
                                        send_dm=True
                                        ),

            "device": inputs.options(ctx,
                                     "How do you play?",
                                     ("Phone/Tablet", "PC", "Spare Phone", "Other"),
                                     send_dm=True
                                     ),
        }

        answers = dict()
        current_question = 0
        keys = tuple(questions.keys())

        # - - - ASK QUESTIONS - - - #

        while current_question < len(keys):
            response = await questions[keys[current_question]]

            # Timed out
            if response is None:
                return

            answers[keys[current_question]] = response

            current_question += 1

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
    bot.add_cog(GuildApplications())
