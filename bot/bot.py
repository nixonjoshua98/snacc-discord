import os
import discord
import asyncpg
import ssl

from discord.ext import commands

from configparser import ConfigParser

from bot.common.queries import ServersSQL

from bot.common import (
	BotConstants,
	DBConnection,
	ServerConfigSQL
)

from bot.structures import HelpCommand


class SnaccBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=self.get_prefix, case_insensitive=True, help_command=HelpCommand())

		self.pool = None

		self.prefixes = dict()

		self.svr_cache = dict()
		self.default_prefix = "!"

	async def on_ready(self):
		await self.wait_until_ready()
		await self.connect_database()
		await self.pool.execute(ServersSQL.TABLE)

		print(f"Bot '{self.user.display_name}' is ready")

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
		await self.wait_until_ready()

		if message.guild is not None:
			return await self.process_commands(message)

	def create_embed(self, *, title: str, desc: str = None, thumbnail: str = None) -> discord.Embed:
		embed = discord.Embed(title=title, description=desc, color=0xff8000)

		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)

		embed.set_footer(text=self.user.display_name, icon_url=self.user.avatar_url)

		return embed

	@property
	def name(self): return self.user.name

	async def update_prefixes(self, message: discord.Message):
		async with self.pool.acquire() as con:
			async with con.transaction():
				svr = await con.fetchrow(ServersSQL.SELECT_SERVER, message.guild.id)

				if svr is None:
					self.prefixes[message.guild.id] = self.default_prefix

					await self.pool.execute(ServersSQL.INSERT_SERVER, message.guild.id, self.default_prefix)

				else:
					self.prefixes[message.guild.id] = svr["prefix"]

		with DBConnection() as con:
			con.cur.execute(ServerConfigSQL.SELECT_SVR, (message.guild.id,))

			self.svr_cache[message.guild.id] = con.cur.fetchone()

	async def get_prefix(self, message: discord.message):
		if self.svr_cache.get(message.guild.id, None) is None:
			await self.update_prefixes(message)

		if self.prefixes.get(message.guild.id, None) is None:
			await self.update_prefixes(message)

		#  return self.prefixes.get(message.guild.id, self.default_prefix)

		try:
			prefix = self.svr_cache[message.guild.id].prefix

			prefix = prefix if prefix is not None else self.default_prefix
		except (AttributeError, KeyError):
			prefix = self.default_prefix

		return commands.when_mentioned_or(prefix)(self, message)

