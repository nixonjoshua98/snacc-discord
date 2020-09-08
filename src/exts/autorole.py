import discord

from discord.ext import commands

from src.common.converters import ServerAssignedRole


class AutoRole(commands.Cog):
	__can_disable__ = False

	def __init__(self, bot):
		self.bot = bot

	def cog_check(self, ctx):
		if not ctx.author.guild_permissions.administrator:
			raise commands.MissingPermissions(("Administrator",))

		return True

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		if not self.bot.debug:
			print("Added listeners: Auto Role")

			self.bot.add_listener(self.on_member_join, "on_member_join")

	async def on_member_join(self, member):
		""" Called when a member joins a server. """

		svr = await self.bot.db["servers"].find_one({"_id": member.guild.id}) or dict()

		try:
			roles = svr.get("roles", dict())

			role = roles.get("bot" if member.bot else "user")

			if role is not None:
				role = member.guild.get_role(role)

				if role is not None:
					await member.add_roles(role)

		except (discord.Forbidden, discord.HTTPException):
			""" We failed to add the role. """

	@commands.group(name="role", invoke_without_command=True, hidden=True)
	async def role_group(self, ctx):
		""" Group. """

	@role_group.command(name="user")
	async def set_user_role(self, ctx, *, role: ServerAssignedRole() = None):
		""" Set the role which is given to every user when they join the server. """

		await self.bot.db["servers"].update_one(
			{"_id": ctx.guild.id},
			{"$set": {"roles.user": getattr(role, "id", 0)}},
			upsert=True
		)

		if role is None:
			await ctx.send(f"User role has been removed")

		else:
			await ctx.send(f"User role set to `{role.name}`")

	@role_group.command(name="bot")
	async def set_bot_role(self, ctx, *, role: ServerAssignedRole() = None):
		""" Set the role which is given to every bot account when they join the server. """

		await self.bot.db["servers"].update_one(
			{"_id": ctx.guild.id},
			{"$set": {"roles.bot": getattr(role, "id", 0)}},
			upsert=True
		)

		if role is None:
			await ctx.send(f"Bot role has been removed")

		else:
			await ctx.send(f"Bot role set to `{role.name}`")


def setup(bot):
	bot.add_cog(AutoRole(bot))
