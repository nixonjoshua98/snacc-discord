import discord

from discord.ext import commands


class Darkness(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return True

	@commands.command(name="members")
	async def get_num_members(self, ctx):
		""" Count the number of guild members in the server. """

		conf = await self.bot.get_server(ctx.guild)

		role = ctx.guild.get_role(conf["member_role"])

		def check(m):
			corp = discord.utils.get(m.roles, name="Darkness Corp")
			inc = discord.utils.get(m.roles, name="Darkness Co")
			co = discord.utils.get(m.roles, name="Darkness Inc")

			return corp or inc or co

		members = list(filter(check, role.members))

		await ctx.send(f"# of users with the ``{role.name}`` role: **{len(members)}**")


def setup(bot):
	bot.add_cog(Darkness(bot))
