import os
import discord

from discord.ext import commands, tasks

import datetime as dt

from src.common import SNACCMAN

from src.structs.help import Help
from src.common.errors import GlobalCheckFail

from src.structs import MongoClient


EXTENSIONS = [
    "errorhandler", "abo",          "empire",
    "quests",       "shop",         "units",
    "battles",      "hangman",      "gambling",
    "bank",         "crypto",       "darkness",
    "moderator",    "misc",         "reminder",
    "autorole",     "serverdoor",   "vote",
    "settings",
]


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=Help())

        self.mongo = MongoClient()

        self.exts_loaded = False

        self.server_cache = dict()

        self._bot_started = None

        self.add_check(self.bot_check)

    @property
    def debug(self):
        return int(os.getenv("DEBUG", 0))

    def has_permission(self, chnl, **perms):
        permissions = chnl.permissions_for(chnl.guild.me)

        return not [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

    @property
    def uptime(self):
        return dt.timedelta(seconds=int((dt.datetime.utcnow() - self._bot_started).total_seconds()))

    @property
    def users(self):
        return set([m for g in self.guilds for m in g.members])

    @tasks.loop(minutes=15.0)
    async def activity_loop(self):
        activity = discord.Game(f"{len(self.users):,} users | {len(self.guilds):,} servers")

        await self.change_presence(status=discord.Status.online, activity=activity)

    async def on_ready(self):
        """ Invoked once the bot is connected and ready to use. """

        self._bot_started = dt.datetime.utcnow()

        self.load_extensions()

        if not self.debug:
            print("Starting loop: Bot Activity")

            self.activity_loop.start()

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

    async def bot_check(self, ctx) -> bool:
        if not self.exts_loaded or ctx.guild is None or ctx.author.bot:
            raise GlobalCheckFail("Bot not ready")

        elif not self.has_permission(ctx.channel, send_messages=True):
            raise GlobalCheckFail(f"I cannot message G: {str(ctx.guild)} C: {ctx.guild.name}")

        elif self.debug and ctx.author.id != SNACCMAN:
            return False

        return True

    def load_extensions(self):
        """ Load all of the extensions for the bot. """

        self.exts_loaded = False

        exts = []

        if not self.debug:
            path = os.path.join(os.getcwd(), "src", "exts", "serverspecific")

            exts = [f"serverspecific.{f[:-3]}" for f in os.listdir(path) if not f.startswith("__")]

        exts.extend(EXTENSIONS)

        for ext in exts:
            try:
                self.load_extension(f"src.exts.{ext}")
            except commands.ExtensionAlreadyLoaded:
                continue

        self.exts_loaded = True

    async def get_prefix(self, message):
        """ Get the prefix for the server/guild from the database/cache. """

        svr = await self.mongo.find_one("servers", {"_id": message.guild.id})

        prefix = "." if self.debug else svr.get("prefix", "!")

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
            await super(Bot, self).on_message(message)

    def run(self):
        super(Bot, self).run(os.getenv("BOT_TOKEN"))


