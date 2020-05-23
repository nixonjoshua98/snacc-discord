import typing

import discord
from discord.ext import commands

from snacc.common.converters import NormalUser, Range


class Moderator(commands.Cog):
	""" Some very basic moderation commands. """

	async def get_mute_role(self, ctx):
		role = discord.utils.get(ctx.guild.roles, name="Muted")

		if role is None:
			try:
				return await ctx.guild.create_role(name="Muted", reason="Required for the Snacc bot.")

			except (discord.Forbidden, discord.HTTPException):
				raise commands.CommandError("I could not find or create the `Muted` role.")

		return role

	@commands.has_permissions(administrator=True)
	@commands.command(name="mute")
	async def mute(self, ctx, target: NormalUser()):
		""" [Admin] Mutes a user, which will delete every message the user sends. """

		role = await self.get_mute_role(ctx)

		try:
			await target.add_roles(role)
		except (discord.HTTPException, discord.Forbidden):
			await ctx.send("I failed to add the `Muted` role to the user.")
		else:
			await ctx.send("User has been muted")

	@commands.has_permissions(administrator=True)
	@commands.command(name="unmute")
	async def unmute(self, ctx, target: NormalUser()):
		""" [Admin] Unmutes a user and allows them to send messages again. """

		role = await self.get_mute_role(ctx)

		try:
			await target.remove_roles(role)
		except (discord.HTTPException, discord.Forbidden):
			await ctx.send("I failed to unmute and remove the `Muted` role from the user.")
		else:
			await ctx.send("User has been unmuted")

	@commands.has_permissions(administrator=True)
	@commands.command(name="purge")
	async def purge(
			self, ctx,
			target: typing.Optional[discord.Member] = None,
			limit: Range(0, 100) = 0):

		""" [Admin] Purge a channel of messages. Optional user can be targeted. """

		def check(m):
			return (target is None or m.author == target) and m.id != ctx.message.id

		deleted = 0

		limit += 1

		try:
			deleted = await ctx.channel.purge(limit=limit, check=check)
		except (discord.HTTPException, discord.Forbidden):
			await ctx.send("Channel purge failed.")

		await ctx.send(f"Deleted {len(deleted)} message(s)")


def setup(bot):
	bot.add_cog(Moderator())
