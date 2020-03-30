import discord

from discord.ext import commands


class SnaccBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=self.get_server_prefix, case_insensitive=True)

        self.default_prefix = "t"

    async def on_ready(self):
        await self.wait_until_ready()

        print(f"Bot '{self.user.name}' is ready")

    async def on_command_error(self, ctx: commands.Context, esc: commands.CommandError):
        print(esc)

    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            await self.process_commands(message)

    def add_cog(self, cog):
        super().add_cog(cog)

        print(f"Cog Loaded: {cog.qualified_name}")

    def get_server_prefix(self, _,  __: discord.message):
        return self.default_prefix
