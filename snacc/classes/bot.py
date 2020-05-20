import os

from discord.ext import commands

from snacc import utils
from snacc.classes.helpcommand import HelpCommand


class SnaccBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

        self.pool = None

        self.server_cache = dict()

    async def on_ready(self):
        self.load_extensions()

        self.pool = await utils.database.create_pool()

        print(f"Bot '{self.user.display_name}' is ready")

    def add_cog(self, cog):
        print(f"Adding Cog: {cog.qualified_name}...", end="")
        super(SnaccBot, self).add_cog(cog)
        print("OK")

    def load_extensions(self):
        print(os.listdir(".\\snacc\\"))
        print(os.listdir(".\\snacc\\exts"))

        for root, dirs, files in os.walk(".\\snacc\\exts"):
            for f in files:
                path = os.path.join(root, f)

                if not f.startswith("__") and not f.endswith("__") and f.endswith(".py"):
                    ext = path[2:].replace("\\", ".")[:-3]

                    self.load_extension(ext)

    async def update_server_cache(self, guild):
        self.server_cache[guild.id] = await utils.settings.get_server_settings(self.pool, guild)

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


