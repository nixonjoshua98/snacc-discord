from discord.ext import commands


class BotUtils(commands.Cog, name="Bot Utils"):
	async def cog_check(self, ctx):
		return await ctx.bot.is_owner(ctx.author)

	@commands.command(name="reload")
	async def reload_ext(self, ctx, ext: str):
		""" [Creator] Reload a bot extension. """

		try:
			ctx.bot.reload_extension(f"snacc.exts.{ext}")
		except Exception as e:
			await ctx.send(e.args[0])
		else:
			await ctx.send(f"`{ext}` has been reloaded.")


def setup(bot):
	bot.add_cog(BotUtils())
