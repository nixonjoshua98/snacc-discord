import os
import ssl
import discord
import asyncpg

from discord.ext import commands

import datetime as dt

from src.common import SNACCMAN

from src.structs.help import Help
from src.structs.context import CustomContext

from src.common.models import ServersM, EmpireM

EXTENSIONS = [
    "errorhandler", "arenastats", "empire", "shop", "tags", "hangman", "gambling",
    "bank", "crypto", "darkness", "moderator", "misc", "serverdoor", "settings"
]


class SnaccBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=Help())

        self.pool = None
        self.exts_loaded = False

        self.server_cache = dict()

        self.add_check(self.bot_check)

        self.before_invoke(self.before_invoke_func)
        self.after_invoke(self.after_invoke_func)

    @property
    def debug(self):
        return int(os.getenv("DEBUG", 0))

    async def on_ready(self):
        """ Invoked once the bot is connected and ready to use. """

        await self.create_pool()
        await self.setup_database()

        self.load_extensions()

        print(f"Bot '{self.user.display_name}' is ready")

    def add_cog(self, cog):
        print(f"Adding {cog.qualified_name}", end=": ")
        super().add_cog(cog)
        print("OK")

    async def is_snacc_owner(self) -> bool:
        if self.owner_id is None:
            app = await self.application_info()

            self.owner_id = app.owner.id

        return self.owner_id == SNACCMAN

    async def setup_database(self):
        """ Create the database tables required for the bot. """

        with open(os.path.join(os.getcwd(), "schema.sql")) as fh:
            await self.pool.execute(fh.read())

    async def bot_check(self, ctx) -> bool:
        if (not self.exts_loaded) or (ctx.guild is None) or ctx.author.bot:
            return False

        svr = await self.get_server_config(ctx.guild)

        bl_chnls, bl_modules = svr["blacklisted_channels"], svr["blacklisted_cogs"]

        if ctx.command.cog is not None and not getattr(ctx.command.cog, "__blacklistable__", True):
            return True

        elif ctx.channel.id in bl_chnls:
            raise commands.CommandError("That command is disabled in this channel.")

        elif ctx.command.cog and ctx.command.cog.qualified_name in bl_modules:
            raise commands.CommandError("That command is disabled in this server.")

        return True

    async def create_pool(self):
        print("Creating connection pool", end="...")

        if self.debug:
            print("local", end="...")

            self.pool = await asyncpg.create_pool(os.getenv("CON_STR"), max_size=15)

        else:
            print("heroku", end="...")

            ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            self.pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"), ssl=ctx, max_size=15)

        print("OK")

    def load_extensions(self):
        """ Load all of the extensions for the bot. """

        self.exts_loaded = False

        for i, ext in enumerate(EXTENSIONS):
            try:
                self.load_extension(f"src.exts.{ext}")

            except commands.ExtensionAlreadyLoaded as e:
                print(e)

        self.exts_loaded = True

    async def update_server_cache(self, guild):
        self.server_cache[guild.id] = await ServersM.fetchrow(self.pool, guild.id)

    async def get_server_config(self, guild, *, refresh: bool = False):
        """ Get the settings from either the cache or the database for a guild. """

        if refresh or self.server_cache.get(guild.id) is None:
            await self.update_server_cache(guild)

        return self.server_cache[guild.id]

    async def get_prefix(self, message):
        """ Get the prefix for the server/guild from the database/cache. """

        svr = await self.get_server_config(message.guild)

        prefix = "." if os.getenv("DEBUG") else svr.get("prefix", "!")

        return commands.when_mentioned_or(prefix)(self, message)

    def embed(self, *, title=None, description=None, thumbnail=None):
        embed = discord.Embed(title=title, description=description, colour=discord.Color.orange())

        embed.timestamp = dt.datetime.utcnow()

        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f"{str(self.user)}", icon_url=self.user.avatar_url)

        return embed

    async def before_invoke_func(self, ctx):
        await EmpireM.set(ctx.bot.pool, ctx.author.id, last_login=dt.datetime.utcnow())

    async def after_invoke_func(self, ctx):
        pass

    async def on_message(self, message):
        if self.exts_loaded and message.guild is not None and not message.author.bot:
            ctx = await self.get_context(message, cls=CustomContext)

            await self.invoke(ctx)

    def run(self):
        super(SnaccBot, self).run(os.getenv("BOT_TOKEN"))


