
from discord.ext import commands

from src.common import checks


class Quests(commands.Cog):

	@checks.has_empire()
	@commands.group(name="quests", aliases=["q"], invoke_without_command=True)
	async def quests_group(self, ctx):
		""" Display the available quests. """

		await ctx.send("!q")

	@checks.has_empire()
	@quests_group.command(name="current", aliases=["c"])
	async def current_quest(self, ctx):
		""" Display the current quest which you have embarked on. """

		await ctx.send("!q current")

	@checks.has_empire()
	@quests_group.command(name="start", aliases=["s"])
	async def start_quest(self, ctx):
		""" Start a new quest. """

		await ctx.send("!q start <int>")


def sertup(bot):
	bot.add_cog(Quests())
