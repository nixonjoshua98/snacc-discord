import discord

from discord.ext import commands

from discord.ext.commands import BucketType

from src.common.converters import Range

from typing import Optional


class Moderator(commands.Cog, command_attrs=(dict(cooldown_after_parsing=True))):
	__blacklistable__ = False

	@commands.has_role("Mod")
	@commands.max_concurrency(1, BucketType.guild)
	@commands.cooldown(1, 30, BucketType.member)
	@commands.command(name="purge", usage="<target=None> <limit=0>")
	async def purge(self, ctx, target: Optional[discord.Member] = None, limit: Range(0, 100) = 0):
		""" Clear a channel of messages. """

		def check(m):
			return target is None or m.author == target

		try:
			deleted = await ctx.channel.purge(limit=limit, check=check)

		except (discord.HTTPException, discord.Forbidden):
			return await ctx.send("Channel purge failed.")

		await ctx.send(f"Deleted {len(deleted):,} message(s)")


def setup(bot):
	bot.add_cog(Moderator())
