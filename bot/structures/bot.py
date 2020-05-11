import discord

from discord.ext import commands
from configparser import ConfigParser

from bot import utils

from bot.common.constants import DEBUGGING

from bot.structures.helpcommand import HelpCommand


class SnaccBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

		self.pool = None

		self.server_cache = dict()

	async def on_ready(self):
		await self.setup_database()
		await self.wait_until_ready()

		print(f"Bot '{self.user.display_name}' is ready")

	async def setup_database(self):
		""" Create the database connection pool and create the tables if they do not already exist. """

		print("Creating PostgreSQL connection pool...", end="")

		self.pool = await utils.database.create_pool()

		await utils.database.create_tables(self.pool)

		print("OK")

	def add_cog(self, cog):
		print(f"Adding Cog: {cog.qualified_name}...", end="")
		super(SnaccBot, self).add_cog(cog)
		print("OK")

	async def on_message(self, message: discord.Message):
		if message.guild is not None and self.is_ready():
			return await self.process_commands(message)

	async def update_server_cache(self, guild: discord.Guild):
		self.server_cache[guild.id] = await utils.settings.get_server_settings(self.pool, guild)

	async def get_server(self, guild):
		if self.server_cache.get(guild.id, None) is None:
			await self.update_server_cache(guild)

		return self.server_cache.get(guild.id, None)

	async def get_prefix(self, message: discord.message):
		if self.server_cache.get(message.guild.id, None) is None:
			await self.update_server_cache(message.guild)

		svr = self.server_cache.get(message.guild.id, dict())

		return "-" if DEBUGGING else svr.get("prefix", "!")

	def run(self):
		config = ConfigParser()

		config.read("./bot/config/bot.ini")

		super(SnaccBot, self).run(config.get("bot", "token"))

