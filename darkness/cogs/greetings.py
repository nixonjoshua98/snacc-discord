from discord.ext import commands

from darkness.common import data_reader


class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._config = data_reader.read_json("server_config.json")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		channel = self.bot.get_channel(self._config["welcome_channel"])

		if channel is not None:
			await channel.send(f"Welcome {member.mention} to the server.")

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		channel = self.bot.get_channel(self._config["welcome_channel"])

		if channel is not None:
			await channel.send(f"{member.display_name} has said farewell to the server.")