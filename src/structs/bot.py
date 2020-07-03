import os
import ssl
import asyncpg

from discord.ext import commands

from src.structs.helpcommand import HelpCommand


class SnaccBot(commands.Bot):
    EXTENSIONS = [
        "errorhandler", "serverdoor", "arenastats", "conquest",
        "applications", "moderator", "wiki", "hangman",
        "gambling", "money", "darkness", "misc", "settings"
    ]

    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

        self.pool = None
        self.exts_loaded = False
        self.server_cache = dict()

        self.add_check(self.on_message_check)

    async def on_ready(self):
        """ Invoked once the bot is connected and ready to use. """

        await self.create_pool()
        await self.setup_database()
        await self.load_extensions()

        print(f"Bot '{self.user.display_name}' is ready")

    async def is_snacc_owner(self) -> bool:
        if self.owner_id is None:
            app = await self.application_info()

            self.owner_id = app.owner.id

        return self.owner_id == 281171949298647041

    async def setup_database(self):
        """ Create the database tables required for the bot. """

        with open(os.path.join(os.getcwd(), "schema.sql")) as fh:
            await self.pool.execute(fh.read())

    async def on_message_check(self, message) -> bool:
        """
        A check which should be called on every 'on_message' listener.

        :param message: The discord message which was received.
        :return bool: Determine if we should listen to the message or not.
        """

        if (not self.exts_loaded) or (message.guild is None) or message.author.bot:
            return False

        return True

    async def on_message(self, message):
        if await self.on_message_check(message):
            await self.process_commands(message)

    async def create_pool(self):
        print("Creating connection pool", end="...")

        if os.getenv("DEBUG"):
            print("local", end="...")

            self.pool = await asyncpg.create_pool(os.getenv("CON_STR"), max_size=15)

        else:
            print("heroku", end="...")

            ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            self.pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"), ssl=ctx, max_size=15)

        print("OK")

    async def load_extensions(self):
        """ Load all of the extensions for the bot. """

        self.exts_loaded = False

        for ext in self.EXTENSIONS:
            print(f"Loading extension {ext}", end="...")

            try:
                self.load_extension(f"src.exts.{ext}")

            except (commands.ExtensionNotFound, commands.ExtensionAlreadyLoaded) as e:
                print(e)

            else:
                print("OK")

        self.exts_loaded = True

    async def update_server_cache(self, guild):
        """
        Update a guild's settings cache.

        :param guild: The discord guild
        """

        settings = self.get_cog("Settings")

        self.server_cache[guild.id] = await settings.get_server_settings(guild)

    async def get_server(self, guild, *, refresh: bool = False):
        """ Get the settings from either the cache or the database for a guild. """

        if refresh or self.server_cache.get(guild.id, None) is None:
            await self.update_server_cache(guild)

        return self.server_cache.get(guild.id, None)

    async def get_prefix(self, message):
        """ Get the prefix for the server/guild from the database. """

        if self.server_cache.get(message.guild.id, None) is None:
            await self.update_server_cache(message.guild)

        svr = self.server_cache.get(message.guild.id, dict())

        prefix = "-" if os.getenv("DEBUG") else svr.get("prefix", "!")

        return commands.when_mentioned_or(prefix)(self, message)

    def run(self):
        super(SnaccBot, self).run(os.getenv("BOT_TOKEN"))


