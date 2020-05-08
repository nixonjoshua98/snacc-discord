import os
import discord

from configparser import ConfigParser

from discord.ext import commands

from bot import utils

from bot.structures.helpcommand import HelpCommand


class SnaccBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

		self.pool = None

		self.server_cache = dict()

		self.default_prefix = "!"

	async def on_ready(self):
		await self.connect_database()
		await self.wait_until_ready()

		print(f"Bot '{self.user.display_name}' is ready")

	async def connect_database(self):
		""" Creates a database connection pool for the Discord bot. """

		print("Creating PostgreSQL connection pool...", end="")

		self.pool = await utils.database.create_pool()

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
		if os.getenv("DEBUG", False):
			return "-"

		if self.server_cache.get(message.guild.id, None) is None:
			await self.update_server_cache(message.guild)

		svr = self.server_cache.get(message.guild.id, dict())

		return svr.get("prefix", self.default_prefix)

	def run(self):
		config = ConfigParser()

		config.read("./bot/config/bot.ini")

		super(SnaccBot, self).run(config.get("bot", "token"))

