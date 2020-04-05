import discord

from discord.ext import commands

from bot.common import (
	BotConstants,
	DBConnection,
	ServerConfigSQL
)

from bot.structures import HelpCommand


class SnaccBot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=SnaccBot.prefix, case_insensitive=True, help_command=HelpCommand())

		self.svr_cache = dict()
		self.default_prefix = "!"

	async def on_ready(self):
		await self.wait_until_ready()

		print(f"Bot '{self.user.display_name}' is ready")

	def add_cog(self, cog):
		print(f"Adding Cog: {cog.qualified_name}...", end="")
		super(SnaccBot, self).add_cog(cog)
		print("OK")

	async def on_command_error(self, ctx: commands.Context, esc):
		if isinstance(esc, commands.UserInputError):
			ctx.command.reset_cooldown(ctx)

		elif isinstance(esc, commands.CommandNotFound):
			return

		return await ctx.send(":x: " + esc.args[0])

	async def on_message(self, message: discord.Message):
		if message.guild is not None:
			return await self.process_commands(message)

	def create_embed(self, *, title: str, desc: str = None, thumbnail: str = None) -> discord.Embed:
		embed = discord.Embed(title=title, description=desc, color=0xff8000)

		if thumbnail is not None:
			embed.set_thumbnail(url=thumbnail)

		embed.set_footer(text=self.user.display_name, icon_url=self.user.avatar_url)

		return embed

	async def update_cache(self, message: discord.Message):
		with DBConnection() as con:
			con.cur.execute(ServerConfigSQL.SELECT_SVR, (message.guild.id,))

			self.svr_cache[message.guild.id] = con.cur.fetchone()

	async def prefix(self, message: discord.message):
		if self.svr_cache.get(message.guild.id, None) is None:
			await self.update_cache(message)

		if BotConstants.DEBUG:
			return "-"

		try:
			prefix = self.svr_cache[message.guild.id].prefix

			return prefix if prefix is not None else self.default_prefix
		except AttributeError:
			return self.default_prefix
