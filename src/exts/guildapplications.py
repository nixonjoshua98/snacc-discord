
from discord.ext import commands

from src import menus


class GuildApplications(commands.Cog):

    @commands.command(name="application", aliases=["app", "join"])
    @commands.max_concurrency(1, commands.BucketType.user)
    async def application(self, ctx):
        if await menus.confirm(ctx, "You are looking to join `Darkness Family`?"):
            await ctx.send("Check your DM. I have started an application with you.")

            inp = await menus.get_input(ctx, "Trophies?", send_dm=True)

            print(inp)




def setup(bot):
    bot.add_cog(GuildApplications())
