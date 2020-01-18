from discord.ext import commands

from darkness.common import data_reader


class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self._greeting_config = data_reader.read_json("greetings_config.json")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		# Welcomes the new user to the server

		channel = member.guild.system_channel

		if channel is not None:
			welcome_msg = self._greeting_config['on_member_join_message'].format(
				member=member,
				guild=member.guild
			)

			await channel.send(welcome_msg)
