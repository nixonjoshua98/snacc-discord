import os

import discord
from discord.ext import commands

from src.common import FileReader


class Greetings(commands.Cog, name="greetings"):
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	async def _send_system_channel(guild: discord.Guild, message: str):
		if guild.system_channel and not os.getenv("DEBUG", False):
			await guild.system_channel.send(message)

	@commands.Cog.listener()
	async def on_guild_join(self, guild: discord.Guild):
		await self._send_system_channel(guild, f"I have arrived!")

		info = await self.bot.application_info()

		await info.owner.send(f"I joined the server **{guild.name}** which is owned by **{guild.owner}**")

	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		await self._send_system_channel(member.guild, f"Welcome {member.mention} to {member.guild.name}!")

		with FileReader("server_settings.json") as file:
			role = file.get_inner_key(str(member.guild.id), "roles", {}).get("default", None)

		discord_role = discord.utils.get(member.guild.roles, id=role)

		if discord_role is not None:
			await member.add_roles(discord_role, atomic=True)

	@commands.Cog.listener()
	async def on_member_remove(self, member: discord.Member):
		await self._send_system_channel(member.guild, f"**{member.display_name}** has left the server :frowning:")
