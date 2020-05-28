import discord
from discord.ext import commands

from typing import Optional

from snacc.common import checks
from snacc.common.converters import NormalUser, Range


class Moderator(commands.Cog):
	""" Some very basic moderation commands. """

	async def cog_check(self, ctx):
		return checks.author_is_admin(ctx)

	async def get_mute_role(self, ctx):
		role = discord.utils.get(ctx.guild.roles, name="Muted")

		if role is None:
			try:
				return await ctx.guild.create_role(name="Muted")

			except (discord.Forbidden, discord.HTTPException):
				raise commands.CommandError("I could not find or create the `Muted` role.")

		return role

	@commands.command(name="mute")
	async def mute(self, ctx, target: NormalUser()):
		""" [Admin] Mutes a user, which will delete every message the user sends. """

		role = await self.get_mute_role(ctx)

		try:
			await target.add_roles(role)
		except (discord.HTTPException, discord.Forbidden):
			return await ctx.send("I failed to mute the target user.")

		await ctx.send("User has been muted")

	@commands.command(name="unmute")
	async def unmute(self, ctx, target: NormalUser()):
		""" [Admin] Unmutes a user and allows them to send messages again. """

		role = await self.get_mute_role(ctx)

		try:
			await target.remove_roles(role)
		except (discord.HTTPException, discord.Forbidden):
			return await ctx.send("I failed to unmute the target user.")

		await ctx.send("User has been unmuted")

	@commands.cooldown(1, 60, commands.BucketType.user)
	@commands.command(name="purge", usage="<target=None> <limit=0>")
	async def purge(self, ctx, target: Optional[discord.Member] = None, limit: Range(0, 100) = 0):
		""" [Admin] Purge a channel of messages. Optional user can be targeted. """

		def check(m):
			return target is None or m.author == target

		try:
			deleted = await ctx.channel.purge(limit=limit, check=check)
		except (discord.HTTPException, discord.Forbidden):
			return await ctx.send("Channel purge failed.")

		await ctx.send(f"Deleted {len(deleted)} message(s)")


def setup(bot):
	bot.add_cog(Moderator())
