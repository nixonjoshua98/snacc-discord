import os

from discord.ext import commands


class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member):
		sys_channel = member.guild.system_channel

		await sys_channel.send(f"Welcome {member.mention} to {member.guild.name}!")

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		sys_channel = member.guild.system_channel

		await sys_channel.send(f"**{member.display_name}** has left the server :frowning:")