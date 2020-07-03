import discord

from discord.ext import commands

from src.common.converters import Range

from typing import Optional


class Moderator(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):

	@commands.has_role("Mod")
	@commands.cooldown(1, 30, commands.BucketType.member)
	@commands.command(name="purge", usage="<target=None> <limit=0>")
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
