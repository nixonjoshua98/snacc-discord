import discord

from discord.ext import commands

from src.common import FileReader

class Greetings(commands.Cog, name="greetings"):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		sys_channel = member.guild.system_channel

		if sys_channel:
			await sys_channel.send(f"Welcome {member.mention} to {member.guild.name}!")

		with FileReader("server_settings.json") as f:
			initial_role_id = f.get(member.guild.id, default_val={}).get("entry_role", None)

		member_role = discord.utils.get(member.guild.roles, id=initial_role_id)

		if member_role is not None:
			await member.add_roles(member_role, atomic=True)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		sys_channel = member.guild.system_channel

		await sys_channel.send(f"**{member.display_name}** has left the server :frowning:")