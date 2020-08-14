
from discord.ext import commands

from src.common.models import ServersM


class Settings(commands.Cog):

	async def cog_after_invoke(self, ctx):
		await ctx.bot.update_server_cache(ctx.message.guild)

	@commands.has_permissions(administrator=True)
	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server-wide prefix. """

		await ServersM.set(ctx.bot.pool, ctx.guild.id, prefix=prefix)

		await ctx.send(f"Server prefix has been updated to `{prefix}`")


def setup(bot):
	bot.add_cog(Settings())
