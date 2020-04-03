import discord
import os

from discord.ext import commands

from src import cogs
from src.common import jsonblob
from src.common import FileReader


class MyBot(commands.Bot):
	def __init__(self):
		super().__init__(
			command_prefix=MyBot.prefix,
			case_insensitive=True,
			help_command=commands.DefaultHelpCommand(no_category="default")
		)

		self.default_prefix = "!"

	async def on_ready(self):
		await self.wait_until_ready()

		print("Bot successfully started")

		jsonblob.download_all()

		for c in cogs.ALL_COGS:
			self.add_cog(c(self))



	def add_cog(self, cog):
		print(f"Adding Cog: {cog.qualified_name}...", end="")
		super(MyBot, self).add_cog(cog)
		print("OK")

	async def on_command_error(self, ctx: commands.Context, esc):
		return await ctx.send(esc)

	async def on_message(self, message: discord.Message):
		if message.guild is not None:
			return await self.process_commands(message)

	def create_embed(self, *, title: str, desc: str = None, thumbnail: str = None):
		embed = discord.Embed(title=title, description=desc, color=0xff8000)

		embed.set_thumbnail(url=thumbnail if thumbnail is not None else self.user.avatar_url)
		embed.set_footer(text=self.user.display_name)

		return embed

	@staticmethod
	def prefix(_: commands.Bot, message: discord.message):
		if os.getenv("DEBUG", False):
			return "-"

		with FileReader("server_settings.json") as server_settings:
			prefix = server_settings.get_inner_key(str(message.guild.id), "prefix", "!")

		return prefix
