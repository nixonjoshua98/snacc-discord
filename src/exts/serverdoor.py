
from discord.ext import commands

from src.common import checks


class ServerDoor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_startup")
    async def on_startup(self):
        if not self.bot.debug:
            print("Added listeners: Server Door")

            self.bot.add_listener(self.on_member_join, "on_member_join")
            self.bot.add_listener(self.on_member_remove, "on_member_remove")

    async def send_system(self, guild, message):
        if guild.system_channel is not None and self.bot.has_permissions(guild.system_channel, send_messages=True):
            await guild.system_channel.send(message)

    @checks.is_admin()
    @commands.command(name="toggledoor")
    async def toggle_door(self, ctx):
        """ Toggle the join and leave messages. """

        svr = await ctx.bot.db["servers"].find_one({"_id": ctx.guild.id}) or dict()

        display_joins = svr.get("display_joins", False)

        await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"display_joins": not display_joins}})

        await ctx.send(f"Join and leave messages: `{'Hidden' if display_joins else 'Shown'}`")

    async def on_member_join(self, member):
        """ Called when a member joins a server. """

        if await self.bot.is_command_enabled(member.guild, self):
            svr = await self.bot.db["servers"].find_one({"_id": member.guild.id}) or dict()

            if svr.get("display_joins", False):
                await self.send_system(member.guild, f"Welcome {member.mention} to {member.guild.name}!")

    async def on_member_remove(self, member):
        """ Called when a member leaves a server. """

        if await self.bot.is_command_enabled(member.guild, self):
            svr = await self.bot.db["servers"].find_one({"_id": member.guild.id}) or dict()

            if svr.get("display_joins", False):
                msg = f"**{str(member)}** " + (f"({member.nick}) " if member.nick else "") + "has left the server"

                await self.send_system(member.guild, msg)


def setup(bot):
    bot.add_cog(ServerDoor(bot))
