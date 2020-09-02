import os
import discord

from discord.ext import commands, tasks

import datetime as dt

from src import utils
from src.common import SNACCMAN
from src.common.errors import GlobalCheckFail

from src.structs.help import Help
from src.structs.mongoclient import MongoClient


EXTENSIONS = [
    "server_741225832994832427",

    "errorhandler",     "arena",            "abo",
    "empire",           "quests",           "shop",
    "units",            "battles",          "hangman",
    "rewards",          "gambling",         "bank",
    "inventory",        "crypto",           "questionnaire",
    "moderator",        "misc",             "support",
    "autorole",         "serverdoor",       "vote",
    "settings"
]


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=Help())

        self.db = MongoClient().snaccV2

        self.exts_loaded = False

        self._bot_started = None

        self.add_check(self.bot_check)

        self.load_extensions()

    @property
    def debug(self):
        return int(os.getenv("DEBUG", 0))

    def has_permissions(self, chnl, **perms):
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

        if self._bot_started is None:
            self.dispatch("startup")

        self._bot_started = dt.datetime.utcnow()

        print(f"Bot '{self.user.display_name}' is ready")

    @commands.Cog.listener("on_startup")
    async def on_startup(self):
        if not self.debug:
            print("Starting loop: Activity")

            self.activity_loop.start()

    def add_cog(self, cog):
        print(f"Adding Cog: {cog.qualified_name}", end="...")
        super().add_cog(cog)
        print("OK")

    async def bot_check(self, ctx) -> bool:
        if not self.exts_loaded or ctx.guild is None or ctx.author.bot:
            raise GlobalCheckFail("Bot not ready")

        elif not self.has_permissions(ctx.channel, send_messages=True):
            raise GlobalCheckFail(f"I cannot message G: {str(ctx.guild)} C: {ctx.channel.name}")

        elif self.debug and ctx.author.id != SNACCMAN:
            raise GlobalCheckFail("Bot is in Debug mode")

        return True

    def load_extensions(self):
        """ Load all of the extensions for the bot. """

        self.exts_loaded = False

        for ext in EXTENSIONS:
            self.load_extension(f"src.exts.{ext}")

        self.exts_loaded = True

    async def get_prefix(self, message):
        """ Get the prefix for the server/guild from the database/cache. """

        svr = await self.db["servers"].find_one({"_id": message.guild.id}) or dict()

        prefix = "." if self.debug else svr.get("prefix", "!")

        return commands.when_mentioned_or(prefix)(self, message)

    def embed(self, *, title=None, description=None, author: discord.User = None, thumbnail=None):
        embed = discord.Embed(title=title, description=description, colour=utils.random_colour())

        embed.timestamp = dt.datetime.utcnow()

        if thumbnail is not None:
            embed.set_thumbnail(url=thumbnail)

        if author is not None:
            embed.set_author(name=author.display_name, icon_url=author.avatar_url)

        embed.set_footer(text=f"{str(self.user)}", icon_url=self.user.avatar_url)

        return embed

    async def on_message(self, message):
        if self.exts_loaded and message.guild is not None and not message.author.bot:
            await super(Bot, self).on_message(message)

    def run(self):
        super(Bot, self).run(os.getenv("BOT_TOKEN"))


