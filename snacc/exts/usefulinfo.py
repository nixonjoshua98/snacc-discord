from discord.ext import commands

from snacc.common import checks


class UsefulInfo(commands.Cog, name="Useful Info"):
	""" Set of commands to update the useful info Embed. """

	@checks.from_guild(666613802657382435)
	@commands.has_permissions(administrator=True)
	@commands.command(name="addlink")
	async def add_useful_link(self, ctx, index: int, name: str, value: str):
		""" [Admin] Add a new field to the useful link embed. """

		channel = ctx.bot.get_channel(666738997468332032)
		message = await channel.fetch_message(708435677511155782)

		embed = message.embeds[0]

		embed.insert_field_at(index, name=name, value=value)

		await message.edit(embed=embed)
		await ctx.send(f"Added the field.")

	@checks.from_guild(666613802657382435)
	@commands.has_permissions(administrator=True)
	@commands.command(name="rmlink")
	async def remove_useful_link(self, ctx, index: int):
		""" [Admin] Remove a field from the useful link embed. """

		channel = ctx.bot.get_channel(666738997468332032)
		message = await channel.fetch_message(708435677511155782)

		embed = message.embeds[0]

		embed.remove_field(index)

		await message.edit(embed=embed)
		await ctx.send(f"Removed the field.")


def setup(bot):
	bot.add_cog(UsefulInfo())
