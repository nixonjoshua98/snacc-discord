import os
import ssl
import asyncpg
import discord

from discord.ext import commands

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

    async def on_message(self, message):
        # Ignore all messages from DM's
        if not message.guild:
            return

        is_muted = discord.utils.get(message.author.roles, name="Muted") is not None

        if is_muted:
            try:
                await message.delete()
            except (discord.HTTPException, discord.Forbidden):
                """ Failed """

        else:
            await self.process_commands(message)

    async def create_pool(self):
        print("Creating connection pool...", end="")

        if os.getenv("DEBUG", False):
            self.pool = await asyncpg.create_pool("postgres://postgres:postgres@localhost:5432/snaccbot", max_size=15)

        else:
            ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            self.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], ssl=ctx, max_size=15)

        print("OK")

    async def load_extensions(self):
        # No commands
        self.load_extension("snacc.exts.errorhandler")
        self.load_extension("snacc.exts.listeners")

        # Has commands
        self.load_extension("snacc.exts.arenastats")
        self.load_extension("snacc.exts.hangman")
        self.load_extension("snacc.exts.usefulinfo")
        self.load_extension("snacc.exts.misc")
        self.load_extension("snacc.exts.moderator")
        self.load_extension("snacc.exts.settings")

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
        super(SnaccBot, self).run(os.environ["SNACC_BOT_TOKEN"])


