import os
import ssl
import asyncpg

print("TEST")

from discord.ext import commands

from snacc import utils
from snacc.classes.helpcommand import HelpCommand


class SnaccBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

        self.pool = None

        self.server_cache = dict()

    async def on_ready(self):
        await self.create_pool()
        await self.load_extensions()

        print(f"Bot '{self.user.display_name}' is ready")

    def add_cog(self, cog):
        print(f"Adding Cog: {cog.qualified_name}...", end="")
        super(SnaccBot, self).add_cog(cog)
        print("OK")

    async def create_pool(self):
        print("Creating connection pool...", end="")

        if os.getenv("DEBUG", False):
            config = utils.load_config("./snacc/config/postgres.ini", "postgres")

            self.pool = await asyncpg.create_pool(**config, max_size=15)

        else:
            ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            self.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], ssl=ctx, max_size=15)

        print("OK")

    async def load_extensions(self):
        for root, dirs, files in os.walk(os.path.join(os.getcwd(), "snacc", "exts")):
            for f in files:
                if not f.startswith("__") and not f.endswith("__") and f.endswith(".py"):
                    ext = f"snacc.exts.{f[:-3]}"

                    self.load_extension(ext)

    async def update_server_cache(self, guild):
        settings = self.get_cog("Settings")

        self.server_cache[guild.id] = await settings.get_server_settings(guild)

    async def get_server(self, guild):
        if self.server_cache.get(guild.id, None) is None:
            await self.update_server_cache(guild)

        return self.server_cache.get(guild.id, None)

    async def get_prefix(self, message):
        if self.server_cache.get(message.guild.id, None) is None:
            await self.update_server_cache(message.guild)

        svr = self.server_cache.get(message.guild.id, dict())

        return "-" if os.getenv("DEBUG", False) else svr.get("prefix", "!")

    def run(self):
        config = utils.load_config("./snacc/config/bot.ini", "bot")

        super(SnaccBot, self).run(config["token"])


