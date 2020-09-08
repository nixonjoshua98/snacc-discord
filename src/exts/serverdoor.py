
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


class ServerDoor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_after_invoke(self, ctx):
        await ctx.bot.update_server_data(ctx.guild)

    @commands.Cog.listener("on_startup")
    async def on_startup(self):
        if not self.bot.debug:
            print("Added listeners: Server Door")

            self.bot.add_listener(self.on_guild_join, "on_guild_join")
            self.bot.add_listener(self.on_member_join, "on_member_join")
            self.bot.add_listener(self.on_member_remove, "on_member_remove")

    async def send_system(self, guild, message):
        if guild.system_channel is not None and self.bot.has_permissions(guild.system_channel, send_messages=True):
            await guild.system_channel.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command(name="toggledoor")
    async def toggle_door(self, ctx):
        """ Toggle the join and leave messages. """

        svr = await ctx.bot.get_server_data(ctx.guild)

        display_joins = svr.get("display_joins", False)

        await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"display_joins": not display_joins}})

        await ctx.send(f"Join and leave messages: `{'Hidden' if display_joins else 'Shown'}`")

    async def on_guild_join(self, guild):
        """ Called when the bot joins a new server. """

        msg = GUILD_JOIN_MESSAGE.format(bot=self.bot, guild=guild)

        await self.send_system(guild, msg)

    async def on_member_join(self, member):
        """ Called when a member joins a server. """

        if not await self.bot.is_command_disabled(member.guild, self):
            svr = await self.bot.get_server_data(member.guild)

            if svr.get("display_joins", False):
                await self.send_system(member.guild, f"Welcome {member.mention} to {member.guild.name}!")

    async def on_member_remove(self, member):
        """ Called when a member leaves a server. """

        if not await self.bot.is_command_disabled(member.guild, self):
            svr = await self.bot.get_server_data(member.guild)

            if svr.get("display_joins", False):
                msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick else "") + "has left the server"

                await self.send_system(member.guild, msg)


def setup(bot):
    bot.add_cog(ServerDoor(bot))
