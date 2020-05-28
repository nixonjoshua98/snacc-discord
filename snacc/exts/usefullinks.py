from discord.ext import commands

from snacc.common import checks

from snacc.common import MAIN_SERVER

USEFUL_LINKS_EMBED = 708435677511155782
USEFUL_LINKS_CHANNEL = 666738997468332032


class UsefulLinks(commands.Cog, name="Useful Links"):
	""" Set of commands to update the useful links Embed. """

	async def cog_check(self, ctx):
		return checks.message_from_guild(ctx, MAIN_SERVER) and checks.author_is_admin(ctx)

	@commands.command(name="addlink")
	async def add_useful_link(self, ctx, index: int, name: str, value: str):
		""" [Admin] Add a new field to the useful link embed. """

		channel = ctx.bot.get_channel(USEFUL_LINKS_CHANNEL)
		message = await channel.fetch_message(USEFUL_LINKS_EMBED)

		embed = message.pages[0]

		embed.insert_field_at(index, name=name, value=value)

		await message.edit(embed=embed)
		await ctx.send(f"Added the field.")

	@commands.command(name="rmlink")
	async def remove_useful_link(self, ctx, index: int):
		""" [Admin] Remove a field from the useful link embed. """

		channel = ctx.bot.get_channel(USEFUL_LINKS_CHANNEL)
		message = await channel.fetch_message(USEFUL_LINKS_EMBED)

		embed = message.pages[0]

		embed.remove_field(index)

		await message.edit(embed=embed)
		await ctx.send(f"Removed the field.")


def setup(bot):
	bot.add_cog(UsefulLinks())
