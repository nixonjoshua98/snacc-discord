
from discord.ext import commands


class Settings(commands.Cog):

	@commands.has_permissions(administrator=True)
	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server-wide prefix. """

		await ctx.bot.mongo.set_one("servers", {"_id": ctx.guild.id}, {"prefix": prefix})

		await ctx.send(f"Server prefix has been updated to `{prefix}`")


def setup(bot):
	bot.add_cog(Settings())
