from discord.ext import commands

from src.common.errors import CogNotFound


class Settings(commands.Cog):
	__can_disable__ = False

	@commands.has_permissions(administrator=True)
	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the server prefix. """

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, {"$set": {"prefix": prefix}}, upsert=True)

		await ctx.send(f"Server prefix has been updated to `{prefix}`")

	@commands.has_permissions(administrator=True)
	@commands.command(name="toggle")
	async def toggle_module(self, ctx: commands.Context, *, module):
		""" Toggle a module between enabled and disabled for the channel. """

		def get_module():
			for key, inst in ctx.bot.cogs.items():
				if module.lower() in (key.lower(), inst.__class__.__name__.lower()):
					return inst

			return None

		if (module := get_module()) is None:
			raise CogNotFound("Module not found.")

		elif len(module.get_commands()) == 0 and not getattr(module, "__can_disable__", True):
			return await ctx.send("This module cannot be disabled.")

		svr = await ctx.bot.db["servers"].find_one({"_id": ctx.guild.id}) or dict()

		disabled_modules = svr.get("disabled_modules", [])

		if (module_name := module.__class__.__name__) in disabled_modules:
			query = {"$pull": {"disabled_modules": module_name}}

			await ctx.send(f"Module **{module_name}** has been enabled.")

		else:
			query = {"$push": {"disabled_modules": module_name}}

			await ctx.send(f"Module **{module_name}** has been disabled.")

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, query, upsert=True)


def setup(bot):
	bot.add_cog(Settings())
