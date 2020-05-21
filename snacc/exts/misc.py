import os

from discord.ext import commands

from snacc.common import checks


class Miscellaneous(commands.Cog):

	@commands.command(name="lines")
	async def lines(self, ctx):
		""" Count the number of lines within the bot. """

		lines = 0

		for root, dirs, files in os.walk("./snacc/"):
			for f in files:
				if f.endswith(".py"):
					path = os.path.join(root, f)

					with open(path, "r") as fh:
						for line in fh.read().splitlines():
							if line:
								lines += 1

		await ctx.send(f"I am made up of **{lines:,}** lines of code.")

	@commands.command(name="source")
	async def send_github(self, ctx):
		""" Bot source code. """

		await ctx.send("https://github.com/nixonjoshua98/discord-snacc-bot")

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
		await ctx.send(f"Added the field at index `{index}`.")

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
		await ctx.send(f"Removed field at index `{index}`.")


def setup(bot):
	bot.add_cog(Miscellaneous())
