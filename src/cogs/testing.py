from discord.ext import commands

from src.common import queries
from src.common import FileReader

from src.common.database import DBConnection

from datetime import datetime


class Testing(commands.Cog, command_attrs=(dict(hidden=True))):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @commands.command(name="convert")
    async def convert(self, ctx):
        import json

        with DBConnection() as con:
            with FileReader("game_stats.json") as f:
                game_stats = f.data()

            for k, v in game_stats.items():
                id_ = int(k)
                date = datetime.strptime(v[0], "%d/%m/%Y %H:%M:%S")
                level = v[1]
                trophies = v[2]

                params = (id_, level, trophies, date)

                con.cur.execute(queries.UPDATE_ABO_STATS_SQL, params)

                await ctx.send(f"JSON -> DB abo {params}")

            with FileReader("server_settings.json") as f:
                config = f.data()

            for k, v in config.items():
                id_ = int(k)
                prefix = v.get("prefix", self.bot.default_prefix)
                roles = json.dumps(v.get("roles", {}))
                channels = json.dumps(v.get("channels", {}))

                params = (id_, prefix, roles, channels)

                con.cur.execute(queries.UPDATE_ENTIRE_SVR_SQL, params)

                await ctx.send(f"JSON -> DB server_config {params}")

            with FileReader("coins.json") as f:
                coins = f.data()

            for k, v in coins.items():
                id_ = int(k)
                bal = v.get("coins", 10)

                params = (id_, bal)

                con.cur.execute(queries.SET_COINS, params)

                await ctx.send(f"JSON -> DB coins {params}")

def setup(bot):
    bot.add_cog(Testing(bot))
