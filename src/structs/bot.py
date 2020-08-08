import os
import ssl
import discord
import asyncpg

from discord.ext import commands, tasks

import datetime as dt

from src.common import SNACCMAN

from src.structs.help import Help
from src.structs.context import CustomContext

from src.common.models import ServersM

EXTENSIONS = [
    "errorhandler", "arenastats", "empire", "quest", "shop", "tags", "hangman",
    "gambling", "bank", "crypto", "darkness", "moderator", "misc", "autorole", "serverdoor", "settings"
]


class SnaccBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=Help())

        self.pool = None
        self.exts_loaded = False

        self.server_cache = dict()

        self.add_check(self.bot_check)

    @property
    def debug(self):
        return int(os.getenv("DEBUG", 0))

    @property
    def users(self):
        return set([m for g in self.guilds for m in g.members])

    def start_activity_loop(self):

        @tasks.loop(minutes=15.0)
        async def activity_loop():
            activity = discord.Game(f"{len(self.users):,} users | {len(self.guilds):,} servers")

            await self.change_presence(status=discord.Status.online, activity=activity)

        if not self.debug:
            print("Starting loop: Bot Activity")

            activity_loop.start()

    async def on_ready(self):
        """ Invoked once the bot is connected and ready to use. """

        await self.create_pool()
        await self.setup_database()

        self.load_extensions()

        self.start_activity_loop()

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

        exts = []

        if not self.debug:
            path = os.path.join(os.getcwd(), "src", "exts", "serverspecific")

            exts = [f"serverspecific.{f[:-3]}" for f in os.listdir(path) if not f.startswith("__")]

        exts.extend(EXTENSIONS)

        for i, ext in enumerate(exts):
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

        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)

        embed.set_footer(text=f"{str(self.user)}", icon_url=self.user.avatar_url)

        return embed

    async def on_message(self, message):
        if self.exts_loaded and message.guild is not None and not message.author.bot:
            ctx = await self.get_context(message, cls=CustomContext)

            await self.invoke(ctx)

    def run(self):
        super(SnaccBot, self).run(os.getenv("BOT_TOKEN"))


