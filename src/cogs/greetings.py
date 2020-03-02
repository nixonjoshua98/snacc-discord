from discord.ext import commands


class Greetings(commands.Cog, name="greetings"):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_member_join(self, member):
		sys_channel = member.guild.system_channel

		if sys_channel:
			return await sys_channel.send(f"Welcome {member.mention} to {member.guild.name}!")

		print(f"{__name__}: No System Channel to send a greetings")

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		sys_channel = member.guild.system_channel

		await sys_channel.send(f"**{member.display_name}** has left the server :frowning:")