import discord

from discord.ext import commands

from bot.common.constants import FEEDBACK_CHANNEL


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command(name="broadcast")
    async def broadcast(self, ctx, *, msg: str):
        """ [Creator] Send a message to each server the bot is in. """

        guilds, sent = ctx.bot.guilds, 0

        for guild in guilds:
            channels = [guild.system_channel] + guild.text_channels

            formatted_msg = msg.format(guild=guild)

            for c in channels:
                try:
                    await c.send(formatted_msg)

                except (discord.Forbidden, discord.HTTPException):
                    pass

                else:
                    sent += 1
                    break

        await ctx.send(f"I sent your message to **{sent}/{len(guilds)}** servers.")

    @commands.cooldown(1, 60 * 60, commands.BucketType.user)
    @commands.command(name="feedback")
    async def feedback(self, ctx, *, msg: str):
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