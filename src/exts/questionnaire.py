
from discord.ext import commands

from src.structs.confirm import Confirm


class Questionnaire(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group(name="questionnaire", aliases=["qu"], hidden=True)
	async def group(self, ctx):
		""" Group command. """


	@group.command(name="create")
	async def create_questionnaire(self, ctx):
		await ctx.send("Creating a Questionnaire for your server.")




def setup(bot):
	bot.add_cog(Questionnaire(bot))
