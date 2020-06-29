
from discord.ext import commands


class Applications(commands.Cog):

	@commands.command(name="test")
	async def test(self, ctx):
		await self.on_member_join(ctx.author)

	@commands.Cog.listener("on_member_join")
	async def on_member_join(self, member):
		pass


def setup(bot):
	bot.add_cog(Applications())
