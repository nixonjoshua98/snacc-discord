import discord

from discord.ext import commands

from snacc.common.converters import Range

from typing import Optional


class Moderator(commands.Cog):

	@commands.has_role("Mod")
	@commands.cooldown(1, 60, commands.BucketType.member)
	@commands.command(name="purge", aliases=["clear"], usage="<target=None> <limit=0>")
	async def purge(self, ctx, target: Optional[discord.Member] = None, limit: Range(0, 100) = 0):
		""" [Mod] Clear a channel of messages. """

		def check(m):
			return target is None or m.author == target

		try:
			deleted = await ctx.channel.purge(limit=limit, check=check)

		except (discord.HTTPException, discord.Forbidden):
			return await ctx.send("Channel purge failed.")

		await ctx.send(f"Deleted {len(deleted)} message(s)")


def setup(bot):
	bot.add_cog(Moderator())
