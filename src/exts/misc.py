import os
import httpx
import discord
import asyncio
import importlib

from discord.ext import commands

from typing import Callable

from src.common import checks
from src.common.converters import PythonCode

from datetime import datetime
from bs4 import BeautifulSoup


class Miscellaneous(commands.Cog):

	@commands.command(name="lines")
	async def lines(self, ctx):
		""" Count the number of lines within the bot. """

		lines = 0

		for root, dirs, files in os.walk("./src/"):
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

		async with httpx.AsyncClient() as client:
			r = await client.get(f"http://dictionary.reference.com/browse/{word}?s=t")

		if r.status_code != httpx.codes.OK:
			return await ctx.send("I failed to query the dictionary.")

		# Soup extracting
		soup = BeautifulSoup(r.content, "html.parser")
		defs = soup.find(class_="css-1urpfgu e16867sm0").find_all(class_="one-click-content css-1p89gle e1q3nk1v4")

		# Create list of definitions
		definitions = [txt for txt in map(lambda ele: ele.text.strip(), defs) if not txt[0].isupper()]
		definitions = [f"{i}. {d}" for i, d in enumerate(definitions, start=1)]

		if len(definitions) > 0:
			# Character limit: 1024
			value = "\n".join(definitions)
			value = value[:1021] + "..." if len(value) > 1024 else value
			embed = discord.Embed(title=word, colour=discord.Color.orange(), url=str(r.url))

			embed.add_field(name="Definition(s)", value=value)

			embed.set_footer(
				text=f"{ctx.bot.user.name} | {datetime.utcnow().strftime('%d/%m/%Y %X')}",
				icon_url=ctx.bot.user.avatar_url
			)

			return await ctx.send(embed=embed)

		await ctx.send("I found no definitions or examples for your query.")

	@commands.command(name="source")
	async def send_github(self, ctx):
		""" Bot source code. """

		await ctx.send("https://github.com/nixonjoshua98/discord-snacc-bot")

	@commands.command(name="invite")
	async def send_bot_invite(self, ctx):
		""" Bot invite link. """

		await ctx.send(
			"Shortened Link\n"
			"https://tinyurl.com/snaccbot\n"
			"Full Length Link\n"
			"https://discord.com/oauth2/authorize?client_id=666616515436478473&scope=bot&permissions=8"
		)

	@commands.command(name="ping")
	async def ping(self, ctx):
		""" Check the bot latency. """

		await ctx.send(f"Pong! {round(ctx.bot.latency * 1000, 3)}ms")

	@checks.snaccman_only()
	@commands.command(name="exec")
	async def exec_code(self, ctx: commands.Context, *, s: PythonCode()):
		"""[Snacc] Dynamically run code. VERY DANGEROUS! """

		path = os.path.join(os.getcwd(), "temp")

		os.makedirs(path, exist_ok=True)

		name = hash(ctx)

		with open(f"temp/{name}.py", "w") as fh:
			fh.write(s)

		module: Callable = importlib.import_module(f"temp.{name}")

		result = "No async run function found."

		if hasattr(module, "run"):
			if asyncio.iscoroutinefunction(module.run):
				result = await module.run(ctx)

		os.remove(f"temp/{name}.py")

		await ctx.send(f'```{result or "OK"}```')


def setup(bot):
	bot.add_cog(Miscellaneous())
