import asyncio
import random

from discord.ext import commands

from src.common import SupportServer

from src.common.converters import Range

from src.structs.confirm import Confirm
from src.structs.reactioncollection import ReactionCollection


class Snaccman(commands.Cog):
	__help_verify_checks__ = True

	async def cog_check(self, ctx):
		if not await ctx.bot.is_owner(ctx.author):
			raise commands.NotOwner()

		return True

	@staticmethod
	async def giveaway_task(ctx, item_name, item_value):
		support_server = ctx.bot.get_guild(SupportServer.ID)

		giveaway_role = support_server.get_role(SupportServer.GIVEAWAY_ROLE)

		destination = support_server.get_channel(SupportServer.GIVEAWAY_CHANNEL)

		embed = ctx.bot.embed(title="Giveaway!", description=f"React :tada: to enter")

		await destination.send(giveaway_role.mention, delete_after=300.0)

		members = await ReactionCollection(ctx.bot, embed, duration=3_600, max_reacts=None).prompt(destination)

		if len(members) >= 2:
			winner = random.choice(members)

			await ctx.bot.db["loot"].insert_one({"user": winner.id, "name": item_name, "value": item_value})

			s = f"Congratulations **{winner.mention}** for winning **- {item_name} -** worth **${item_value:,}!**"

			await destination.send(s)

	@commands.command(name="giveaway")
	async def giveaway(self, ctx, value: Range(0, None), *, item):
		""" Create a giveaway in the support server. """

		resp = await Confirm(f"Create a giveaway with **{item}** worth **${value:,}** as the reward?").prompt(ctx)

		if not resp:
			return await ctx.send("Giveaway aborted")

		asyncio.create_task(self.giveaway_task(ctx, item, value))

		await ctx.send("I have started a giveaway in the support server!")



def setup(bot):
	bot.add_cog(Snaccman())
