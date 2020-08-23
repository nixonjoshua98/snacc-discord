import discord

from discord.ext import commands

from datetime import datetime

from src import inputs
from src.common import DarknessServer, checks


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
                                                             "0-3 hours",
                                                             "4-6 hours",
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

        channel = ctx.bot.get_channel(DarknessServer.APP_CHANNEL)

        embed = discord.Embed(title="Guild Application", colour=discord.Color.orange())

        for k, v in answers.items():
            embed.add_field(name=k.title(), value=v, inline=False)

        embed.timestamp = datetime.utcnow()

        embed.set_footer(text=f"{str(ctx.author)}", icon_url=ctx.author.avatar_url)

        await channel.send(embed=embed)

    @checks.snaccman_only()
    @checks.main_server_only()
    @commands.command(name="champ")
    async def event_champion(self, ctx, user: discord.Member = None):
        event_role = discord.utils.get(ctx.guild.roles, id=DarknessServer.EVENT_ROLE)
        event_chnl = discord.utils.get(ctx.guild.channels, id=DarknessServer.FAME_CHANNEL)

        for m in event_role.members:
            await m.remove_roles(event_role)

        if user is None:
            return await ctx.send("Event role has been removed from all users.")

        await user.add_roles(event_role)

        await ctx.send(
            f"Congratulations **{str(user)}** on winning the event! "
            f"You have been given the {event_role.mention} role, "
            f"which allows you to send a few messages in {event_chnl.mention} "
            f"for everyone to see."
        )




def setup(bot):
    bot.add_cog(Darkness())
