import os
import discord
import asyncpg
import ssl

from discord.ext import commands

from configparser import ConfigParser

from bot.common.queries import ServersSQL, BankSQL, HangmanSQL

from bot.structures import HelpCommand


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

	async def get_context(self, message, *, cls=commands.Context):
		return await super().get_context(message, cls=cls)

	async def connect_database(self):
		""" Creates database connection pool for the Discord bot. """

		# Local database
		if os.getenv("DEBUG", False):
			config = ConfigParser()
			config.read("postgres.ini")

			self.pool = await asyncpg.create_pool(**dict(config.items("postgres")), command_timeout=60)

		# Heroku database
		else:
			# SSL stuff
			ctx = ssl.create_default_context(cafile="./rds-combined-ca-bundle.pem")
			ctx.check_hostname = False
			ctx.verify_mode = ssl.CERT_NONE

			self.pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], ssl=ctx, command_timeout=60)

		print("Created PostgreSQL connection pool")

	def add_cog(self, cog):
		print(f"Adding Cog: {cog.qualified_name}...", end="")
		super(SnaccBot, self).add_cog(cog)
		print("OK")

	async def on_command_error(self, ctx: commands.Context, esc):
		if isinstance(esc, commands.UserInputError):
			ctx.command.reset_cooldown(ctx)

		elif isinstance(esc, commands.CommandNotFound):
			return

		return await ctx.send(esc.args[0])

	async def on_message(self, message: discord.Message):
		if message.guild is not None:
			return await self.process_commands(message)

	async def update_prefixes(self, message: discord.Message):
		if self.pool is None:
			return

		settings = self.get_cog("Settings")

		svr = await settings.get_server(message.guild)

		self.prefixes[message.guild.id] = svr["prefix"]

	async def get_prefix(self, message: discord.message):
		if self.prefixes.get(message.guild.id, None) is None:
			await self.update_prefixes(message)

		return self.prefixes.get(message.guild.id, self.default_prefix)

