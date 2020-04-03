import discord
import random
import asyncio

from discord.ext import commands

from src.common import checks
from src.common import functions
from src.common import converters
from src.common import FileReader

from src.common.database import DBConnection

from datetime import datetime


class Testing(commands.Cog, name="testing"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="abo2db")
    async def abo2db(self, ctx):
        with FileReader("game_stats.json") as f:
            data = f.data()

        with DBConnection() as con:
            for k, v in data.items():
                id_ = int(k)
                date = datetime.strptime(v[0], "%d/%m/%Y %H:%M:%S")
                level = v[1]
                trophies = v[2]

                params = (id_, level, trophies, date)

                con.cur.execute(con.get_query("update-user-abo.sql"), params)


def setup(bot):
    bot.add_cog(Testing(bot))
