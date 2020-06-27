import discord

from discord.ext import commands

from typing import Tuple

from snacc.common import MainServer, checks


class UsefulLinks(commands.Cog, name="Useful Links"):
	""" Set of commands to update the useful links Embed. """

	async def cog_check(self, ctx):
		return checks.message_from_guild(ctx, MainServer.ID) and checks.author_is_admin(ctx)

	async def get_embed(self, ctx) -> Tuple[discord.Message, discord.Embed]:
		""" Get the useful links message. """

		channel = ctx.bot.get_channel(MainServer.USEFUL_LINKS_CHANNEL)

		message = await channel.fetch_message(MainServer.USEFUL_LINKS_EMBED)

		return message, message.embeds[0]

	@commands.command(name="addlink")
	async def add_useful_link(self, ctx, index: int, name: str, value: str):
		""" [Admin] Add a new field to the useful link embed. """

		message, embed = await self.get_embed(ctx)

		embed.insert_field_at(index, name=name, value=value)

		await message.edit(embed=embed)

		await ctx.send(f"Added the field.")

	@commands.command(name="rmlink")
	async def remove_useful_link(self, ctx, index: int):
		""" [Admin] Remove a field from the useful link embed. """

		message, embed = await self.get_embed(ctx)

		embed.remove_field(index)

		await message.edit(embed=embed)
		await ctx.send(f"Removed the field.")


def setup(bot):
	bot.add_cog(UsefulLinks())
