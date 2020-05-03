import os
import discord
import asyncpg

from discord.ext import commands

from bot.common import utils
from bot.structures.helpcommand import HelpCommand


class SnaccBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

		self.pool = None

		self.prefixes = dict()

		self.default_prefix = "!"

	async def on_ready(self):
		await self.connect_database()
		await self.wait_until_ready()

		print(f"Bot '{self.user.display_name}' is ready")

	async def connect_database(self):
		""" Creates a database connection pool for the Discord bot. """

		if os.getenv("DEBUG", False):
			config = utils.read_config_section("./bot/config/postgres.ini", "postgres")

			self.pool = await asyncpg.create_pool(**dict(config), command_timeout=60, max_size=20)

		else:
			ctx = utils.create_heroku_database_ssl()

			self.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], ssl=ctx, command_timeout=60, max_size=20)

		print("Created PostgreSQL connection pool")

	def add_cog(self, cog):
		print(f"Adding Cog: {cog.qualified_name}...", end="")
		super(SnaccBot, self).add_cog(cog)
		print("OK")

	async def on_command_error(self, ctx: commands.Context, esc):
		if isinstance(esc, commands.CommandNotFound):
			return

		return await ctx.send(esc.args[0])

	async def on_message(self, message: discord.Message):
		if message.guild is not None and self.is_ready():
			return await self.process_commands(message)

	async def update_prefixes(self, message: discord.Message):
		settings = self.get_cog("Settings")

		svr = await settings.get_server_settings(message.guild)

		self.prefixes[message.guild.id] = svr["prefix"]

	async def get_prefix(self, message: discord.message):
		if os.getenv("DEBUG", False):
			return "-"

		if self.prefixes.get(message.guild.id, None) is None:
			await self.update_prefixes(message)

		return self.prefixes.get(message.guild.id, self.default_prefix)

