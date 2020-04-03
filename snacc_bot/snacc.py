import discord

from discord.ext import commands


class SnaccBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_server_prefix,
            case_insensitive=True,
            help_command=commands.DefaultHelpCommand(no_category="Default")
        )

        self.default_prefix = "!"

    async def on_ready(self):
        await self.wait_until_ready()

        print(f"Bot '{self.user.name}' is ready")

    async def on_command_error(self, ctx: commands.Context, esc):
        return await ctx.send(esc)

    async def on_message(self, message: discord.Message):
        if message.guild is not None:
            await self.process_commands(message)

    def add_cog(self, cog):
        super().add_cog(cog)

        print(f"Cog Loaded: {cog.qualified_name}")

    def get_server_prefix(self, _,  __: discord.message):
        return self.default_prefix

    def create_embed(self, *, title: str, desc: str = None, thumbnail: str = None):
        embed = discord.Embed(title=title, description=desc, color=0xff8000)

        embed.set_thumbnail(url=thumbnail if thumbnail is not None else self.user.avatar_url)
        embed.set_footer(text=self.user.display_name)

        return embed
