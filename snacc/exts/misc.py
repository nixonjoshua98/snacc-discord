import os
import httpx

import discord
from discord.ext import commands

from datetime import datetime
from bs4 import BeautifulSoup

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

	@commands.command(name="whatis")
	async def what_is_this(self, ctx, word: str):
		""" Look for a word definition. """

		word = word.lower()

		async def send_request(url_: str):
			async with httpx.AsyncClient() as client:
				return await client.get(url_)

		url = f"http://dictionary.reference.com/browse/{word}?s=t"

		r = await send_request(url)

		if r.status_code != httpx.codes.OK:
			return await ctx.send("I found not definitions or examples for your query.")

		soup = BeautifulSoup(r.content, "html.parser")

		entry = soup.find(class_="css-1urpfgu e16867sm0")
		defs = entry.find_all(class_="one-click-content css-1p89gle e1q3nk1v4")

		definitions = [txt for txt in map(lambda ele: ele.text.strip(), defs) if not txt[0].isupper()]
		definitions = [f"{i}. {d}" for i, d in enumerate(definitions, start=1)]

		if len(definitions) > 0:
			today = datetime.today().strftime('%d/%m/%Y %X')

			embed = discord.Embed(title=word, colour=discord.Color.orange(), url=url)

			embed.set_footer(text=f"{ctx.bot.user.name} | {today}", icon_url=ctx.bot.user.avatar_url)

			value = "\n".join(definitions)
			value = value[:1021] + "..." if len(value) > 1024 else value

			embed.add_field(name="Definitions", value=value)

			await ctx.send(embed=embed)

		else:
			await ctx.send("I found not definitions or examples for your query.")

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
	bot.add_cog(Miscellaneous())
