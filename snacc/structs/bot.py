import os
import ssl
import asyncpg
import discord

from discord.ext import commands

from snacc.structs.helpcommand import HelpCommand

from snacc.common.queries import ArenaStatsSQL, HangmanSQL, ServersSQL


class SnaccBot(commands.Bot):
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

    def add_cog(self, cog):
        """ [Override] Adds a cog and logs it to the console. """

        print(f"Adding Cog: {cog.qualified_name}...", end="")
        super(SnaccBot, self).add_cog(cog)
        print("OK")

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

        elif await self.is_user_muted(message):
            return False

        return True

    async def is_user_muted(self, message) -> bool:
        """
        Returns a boolean showing if the user is muted, as well as deleting their message if they are muted.

        :param message: The discord message
        :return bool: Returns if the user is muted.
        """

        is_muted = discord.utils.get(message.author.roles, name="Muted") is not None

        # Attempt to delete the message if they are muted
        if is_muted:
            try:
                await message.delete()
            except (discord.HTTPException, discord.Forbidden):
                """ Failed """

        return is_muted

    async def on_message(self, message):
        if await self.on_message_check(message):
            await self.process_commands(message)

    async def create_pool(self):
        print("Creating connection pool...", end="")

        if os.getenv("DEBUG", False):
            # Local
            self.pool = await asyncpg.create_pool(os.environ["CON_STR"], max_size=15)

        else:
            # Heroku
            ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            self.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], ssl=ctx, max_size=15)

        print("OK")

    async def load_extensions(self):
        """ Load all of the extensions for the bot. """

        self.exts_loaded = False

        self.load_extension("snacc.exts.errorhandler")
        self.load_extension("snacc.exts.listeners")
        self.load_extension("snacc.exts.onmessage")

        self.load_extension("snacc.exts.arenastats")
        self.load_extension("snacc.exts.hangman")
        self.load_extension("snacc.exts.usefullinks")
        self.load_extension("snacc.exts.moderator")
        self.load_extension("snacc.exts.misc")
        self.load_extension("snacc.exts.settings")

        self.exts_loaded = True

    async def update_server_cache(self, guild):
        """
        Update a guild's settings cache.

        :param guild: The discord guild
        """

        settings = self.get_cog("Settings")

        self.server_cache[guild.id] = await settings.get_server_settings(guild)

    async def get_server(self, guild):
        """ Get the settings from either the cache or the database for a guild. """

        if self.server_cache.get(guild.id, None) is None:
            await self.update_server_cache(guild)

        return self.server_cache.get(guild.id, None)

    async def get_prefix(self, message):
        """ Get the prefix for the server/guild from the database. """

        if self.server_cache.get(message.guild.id, None) is None:
            await self.update_server_cache(message.guild)

        svr = self.server_cache.get(message.guild.id, dict())

        prefix = "?" if os.getenv("DEBUG", False) else svr.get("prefix", "!")

        return commands.when_mentioned_or(prefix)(self, message)

    def run(self):
        super(SnaccBot, self).run(os.environ["SNACC_BOT_TOKEN"])


