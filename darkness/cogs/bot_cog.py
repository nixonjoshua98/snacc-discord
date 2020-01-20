from discord.ext import commands

from darkness.common import data_reader
from darkness.common import myjson


class BotCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.is_owner()
	@commands.command(name="prefix", description="Set the prefix for the bot", hidden=True)
	async def prefix(self, ctx, prefix: str):
		# Sets the bot prefix

		if len(prefix) != 1:
			await ctx.send("Prefix must be a single character")
		else:
			data_reader.write_json_keys("bot_config.json", prefix=prefix)

			self.bot.command_prefix = prefix

			await ctx.send(f"My command prefix has been set to {prefix}")

	@commands.is_owner()
	@commands.command(name="backup", hidden=True)
	async def backup(self, ctx):

		msg = await ctx.send("Starting backup, this will block other commands")

		ok = myjson.upload_all()

		if ok:
			await msg.edit(content="Data backed up successfully")
		else:
			await msg.edit(content="Not all data was backed up")

