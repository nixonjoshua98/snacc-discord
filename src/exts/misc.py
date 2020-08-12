import os
import httpx
import discord
import psutil
import cpuinfo

from discord.ext import commands

import datetime as dt
from bs4 import BeautifulSoup

from src.structs.textpage import TextPage


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
			return await ctx.send(f"I failed to lookup your query. Status Code: {r.status_code}")

		# Soup extracting
		soup = BeautifulSoup(r.content, "html.parser")
		defs = soup.find(class_="css-1urpfgu e16867sm0").find_all(class_="one-click-content css-1p89gle e1q3nk1v4")

		# Create list of definitions
		definitions = [txt for txt in map(lambda ele: ele.text.strip(), defs) if not txt[0].isupper()]
		definitions = [f"{i}. {d}" for i, d in enumerate(definitions, start=1)]

		if len(definitions) > 0:
			value = "\n".join(definitions)
			value = value[:1021] + "..." if len(value) > 1024 else value

			embed = discord.Embed(title=word, colour=discord.Color.orange(), url=str(r.url))

			embed.timestamp = dt.datetime.utcnow()

			embed.add_field(name="Definition(s)", value=value)

			embed.set_footer(text=ctx.bot.user.name, icon_url=ctx.bot.user.avatar_url)

			return await ctx.send(embed=embed)

		await ctx.send("I found no definitions or examples for your query.")

	@commands.command(name="invite")
	async def send_bot_invite(self, ctx):
		""" Bot invite link. """

		url = "https://discord.com/oauth2/authorize?client_id=666616515436478473&scope=bot&permissions=1544023127"

		await ctx.send(url)

	@commands.command(name="ping")
	async def ping(self, ctx):
		""" Check the bot latency. """

		await ctx.send(f"Pong! {round(ctx.bot.latency * 1000, 3)}ms")

	@commands.command(name="support")
	async def support(self, ctx):
		""" Link to the support server. """

		await ctx.send("https://discord.gg/QExQuvE")

	@commands.command(name="bot")
	async def show_stats(self, ctx):
		def get_system():
			memory = psutil.virtual_memory()
			cpu = cpuinfo.get_cpu_info()

			system = {
				"CPU": {
					"Brand": cpu["brand"],
					"Base Clock": cpu["hz_actual"],
					"Logical Cores": psutil.cpu_count(),
					"Utilisation": f"{round(psutil.cpu_percent(), 1)}%",
				},

				"Memory": {
					"Total": f"{round(memory.total / (1024 ** 3), 1)}GB",
					"Used": f"{round(memory.used / (1024 ** 3), 1)}GB",
					"Available": f"{round(memory.available / (1024 ** 3), 1)}GB"
				},
			}

			return system

		embed = ctx.bot.embed(title="Bot Stats", thumbnail=ctx.author.avatar_url)

		for k, v in get_system().items():
			if isinstance(v, dict):
				embed.add_field(name=k, value="\n".join([f"{k2}: **{v2}**" for k2, v2 in v.items()]), inline=False)

				continue

			embed.add_field(name=k, value=v, inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="cooldowns", aliases=["cd"])
	async def cooldowns(self, ctx):
		""" Display your command cooldowns. """

		page = TextPage(title="Your Cooldowns", headers=("Command", "Cooldown"))

		for name, inst in ctx.bot.cogs.items():
			for cmd in inst.walk_commands():

				if cmd._buckets._cooldown:
					try:
						if not await cmd.can_run(ctx):
							continue
					except commands.CommandError:
						continue

					current = ctx.message.created_at.replace(tzinfo=dt.timezone.utc).timestamp()
					bucket = cmd._buckets.get_bucket(ctx.message, current)

					if bucket._tokens == 0:
						retry_after = bucket.per - (current - bucket._window)

						page.add_row((cmd.name, dt.timedelta(seconds=int(retry_after))))

		if len(page.rows) == 0:
			page.set_footer("You have no active cooldowns")

		await ctx.send(page.get())


def setup(bot):
	bot.add_cog(Miscellaneous())
