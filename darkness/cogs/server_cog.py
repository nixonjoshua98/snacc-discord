import validators

from discord.ext import commands

from darkness.common import data_reader


class Server(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="size", description="Number of members in the server")
	async def size(self, ctx):
		# Returns the server size
		await ctx.send(f"This server has ``{ctx.guild.member_count}`` members")

	@commands.group(name="invite", description="Server invite link")
	async def invite(self, ctx):
		# Returns the invite link for the server

		if ctx.invoked_subcommand is None:
			server_config = data_reader.read_json("server_config.json")

			await ctx.send(server_config["invite_link"])

	@commands.is_owner()
	@invite.group(name="set")
	async def set_invite(self, ctx, url: str):
		if validators.url(url):
			data_reader.write_json_keys("server_config.json", invite_link=url)

			await ctx.send(f"``{ctx.message.author.display_name}`` has set the server invite link")

		else:
			await ctx.send("Invite link is not valid")
