from discord.ext import commands

from darkness.common import data_reader


class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member):
		# Welcomes the new user to the server

		channel = member.guild.system_channel

		if channel is not None:
			welcome_msg = "Welcome {member.mention} to {guild.name}! Let us know you are here in #non-member-chat!".format(
				member=member,
				guild=member.guild
			)

			await channel.send(welcome_msg)
