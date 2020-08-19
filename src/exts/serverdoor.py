import discord

from discord.ext import commands


GUILD_JOIN_MESSAGE = """
The infamous **{bot.user.name}** has graced your ~~lowly~~ server!

Please look at my `!help`

**!create** to start your Empire adventure!
**!quest** to view your quests (hint: buy **!units** with a power rating to increase your success rate)
Play a game of **!hangman** (view the leaderboard **!hlb**)
**Moderation** commands require a `Mod` role.
Buy Crypto using **!c** and **!c buy/sell**

__Join the **NEW** support server__
https://discord.gg/QExQuvE
"""


class ServerDoor(commands.Cog, name="Server Door"):

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    async def send_message(guild, message):
        channels = [guild.system_channel] + guild.text_channels

        for c in channels:
            try:
                await c.send(message)

            except (discord.Forbidden, discord.HTTPException):
                continue

            break

    @commands.has_permissions(administrator=True)
    @commands.command(name="toggledoor")
    async def toggle_door(self, ctx):
        """ Toggle the messages posted when a member joins or leaves the server. """

        svr = await self.bot.mongo.find_one("servers", {"_id": ctx.guild.id})

        display_joins = svr.get("display_joins", False)

        await ctx.bot.mongo.update_one("servers", {"_id": ctx.guild.id}, {"display_joins": not display_joins})

        await ctx.send(f"Server door: {'`Hidden`' if display_joins else '`Shown`'}")

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild):
        """ Called when the bot joins a new server. """

        msg = GUILD_JOIN_MESSAGE.format(bot=self.bot, guild=guild)

        await self.send_message(guild, msg)

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        """ Called when a member joins a server. """

        svr = await self.bot.mongo.find_one("servers", {"_id": member.guild.id})

        if svr.get("display_joins"):
            await self.send_message(member.guild, f"Welcome {member.mention} to {member.guild.name}!")

    @commands.Cog.listener("on_member_remove")
    async def on_member_remove(self, member):
        """ Called when a member leaves a server. """

        svr = await self.bot.mongo.find_one("servers", {"_id": member.guild.id})

        if svr.get("display_joins"):
            msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick else "") + "has left the server"

            await self.send_message(member.guild, msg)


def setup(bot):
    if not bot.debug:
        bot.add_cog(ServerDoor(bot))
