from discord.ext import commands

from bot.common.constants import FEEDBACK_CHANNEL


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="feedback")
    async def feedback(self, ctx, *, msg: str):
        """ Submit bot feedback. """

        msg = msg.strip()

        if len(msg) < 16:
            return await ctx.send("Your message is too short")

        channel = ctx.bot.get_channel(FEEDBACK_CHANNEL)

        msg = f"**User:** {str(ctx.author)}\n" \
              f"**Server:** {ctx.guild.name}\n" \
              f"**Feedback: **{msg}\n" \
              f"- - - - - - - - - -"

        await channel.send(msg[0:2000])

        await ctx.send("Thank you for the feedback!")



def setup(bot):
    bot.add_cog(Misc(bot))