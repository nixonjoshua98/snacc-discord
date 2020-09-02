
from discord.ext import commands


class Settings(commands.Cog):

	@commands.has_permissions(administrator=True)
	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server prefix. """

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}, upsert=True)

		await ctx.send(f"Server prefix has been updated to `{prefix}`")


def setup(bot):
	bot.add_cog(Settings())
