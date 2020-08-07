
from discord.ext import commands

from src.common.models import ServersM
from src.common.converters import ServerAssignedRole


class Settings(commands.Cog):

	def cog_check(self, ctx):
		if not ctx.author.guild_permissions.administrator:
			raise commands.MissingPermissions(("Administrator",))

		return True

	async def cog_after_invoke(self, ctx):
		await ctx.bot.update_server_cache(ctx.message.guild)

	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server-wide prefix. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, prefix=prefix)

		await ctx.send(f"Server prefix has been updated to `{prefix}`")

	@commands.group(name="role", invoke_without_command=True, hidden=True)
	async def role_group(self, ctx):
		await ctx.send(f"Use either {ctx.prefix}role bot <role> or {ctx.prefix}role user <role>")

	@role_group.command(name="user")
	async def set_user_role(self, ctx, *, role: ServerAssignedRole() = None):
		""" Set the role which is given to every user when they join the server. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, user_role=getattr(role, "id", 0))

		if role is None:
			await ctx.send(f"User role has been removed")

		else:
			await ctx.send(f"User role set to `{role.name}`")

	@role_group.command(name="bot")
	async def set_bot_role(self, ctx, *, role: ServerAssignedRole() = None):
		""" Set the role which is given to every bot account when they join the server. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, bot_role=getattr(role, "id", 0))

		if role is None:
			await ctx.send(f"Bot role has been removed")

		else:
			await ctx.send(f"Bot role set to `{role.name}`")


def setup(bot):
	bot.add_cog(Settings())
