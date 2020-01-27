from discord.ext import commands

from darkness.common.constants import NON_MEMBER_CHANNEL


class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member):
		sys_channel = member.guild.system_channel

		chat_channel = member.guild.get_channel(NON_MEMBER_CHANNEL)

		await sys_channel.send(f"Welcome {member.mention}, talk to us in {chat_channel.mention}!")