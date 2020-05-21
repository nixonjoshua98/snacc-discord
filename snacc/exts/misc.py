import os
import httpx

import discord
from discord.ext import commands

from datetime import datetime

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
	async def what_is_this(self, ctx, query):
		async def send_request(query_: str):
			url = f"https://od-api.oxforddictionaries.com/api/v2/entries/en-us/{query_.lower()}"

			id_, key = os.environ["OXFORD_ID"], os.environ["OXFORD_KEY"]

			async with httpx.AsyncClient() as client:
				return await client.get(url, headers={"app_id": id_, "app_key": key})

		r = await send_request(query)

		if r.status_code != 200:
			return await ctx.send("I failed to look your query up.")

		results = r.json()

		today = datetime.today().strftime('%d/%m/%Y %X')

		embed = discord.Embed(title=f"What is '{results['word']}'?", colour=discord.Color.orange())

		embed.set_footer(text=f"{ctx.bot.user.name} | {today}", icon_url=ctx.bot.user.avatar_url)

		definitions, examples = [], []

		top_entry = results["results"][0]["lexicalEntries"][0]["entries"][0]

		for sense in top_entry["senses"][:3]:
			definitions.extend(f"{deff}" for deff in sense["definitions"])
			examples.extend(f"{example['text']}" for example in sense.get("examples", []))

		if len(definitions) > 0:
			definitions = [f"{i}. {ele}" for i, ele in enumerate(definitions, start=1)]
			embed.add_field(name="Definition(s)", value="\n".join(definitions), inline=False)

		if len(examples) > 0:
			examples = [f"{i}. {ele}" for i, ele in enumerate(examples, start=1)]
			embed.add_field(name="Example(s)", value="\n".join(examples), inline=False)

		if len(examples) > 0 and len(definitions) > 0:
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
