import asyncio
import random

from discord.ext import commands

from src.common import SupportServer

from src.common.converters import Range

from src.structs.confirm import Confirm
from src.structs.reactioncollection import ReactionCollection


class Support(commands.Cog):
	__help_verify_checks__ = True

	def __init__(self, bot):
		self.bot = bot

	@commands.is_owner()
	@commands.command(name="giveaway")
	async def giveaway_command(self, ctx, value: Range(0, None), *, item):
		""" Start a giveaway in the support server. """

		resp = await Confirm(f"Create a giveaway with **{item}** worth **${value:,}** as the reward?").prompt(ctx)

		if not resp:
			return await ctx.send("Giveaway aborted")

		await ctx.send("I have started a giveaway in the support server!")

		asyncio.create_task(Giveaway(self.bot, item, value).send())

	@commands.command(name="support")
	async def support(self, ctx):
		""" Link to the support server. """

		await ctx.send("https://discord.gg/QExQuvE")


class Giveaway:
	def __init__(self, bot, name, value):
		self.bot = bot

		self.item_name = name
		self.item_value = value

		self.destination = None

	async def send(self):
		support_server = self.bot.get_guild(SupportServer.ID)

		giveaway_role = support_server.get_role(SupportServer.GIVEAWAY_ROLE)

		self.destination = chnl = support_server.get_channel(SupportServer.GIVEAWAY_CHANNEL)

		embed = self.bot.embed(title="Giveaway!", description=f"React :tada: to enter")

		await chnl.send(giveaway_role.mention, delete_after=300.0)

		members = await ReactionCollection(self.bot, embed, duration=3_600, max_reacts=None).prompt(chnl)

		if len(members) >= 2:
			await self.on_giveaway_end(members)

	async def on_giveaway_end(self, members):
		winner = random.choice(members)

		await self.bot.db["loot"].insert_one({"user": winner.id, "name": self.item_name, "value": self.item_value})

		await self.destination.send(
			f"Congratulations **{winner.mention}** for winning **- {self.item_name} -** worth **${self.item_value:,}!**"
		)


def setup(bot):
	bot.add_cog(Support(bot))
