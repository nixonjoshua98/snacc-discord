import discord
import asyncio
import random

from discord.ext import commands

from bot.common.constants import DARKNESS_GUILD


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        await self.rgb_loop()

    async def cog_check(self, ctx):
        return ctx.guild.id == DARKNESS_GUILD

    async def rgb_loop(self):
        def get_colour():
            return discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        guild = self.bot.get_guild(DARKNESS_GUILD)
        role: discord.Role = discord.utils.get(guild.roles, name="RGB") if guild is not None else None

        while True:
            if role is None:
                continue

            try:
                await role.edit(colour=get_colour())

            except (discord.Forbidden, discord.HTTPException) as e:
                pass

            await asyncio.sleep(60 * 60)


def setup(bot):
    bot.add_cog(Misc(bot))
