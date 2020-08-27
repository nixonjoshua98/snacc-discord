import os
import httpx

from discord.ext import commands

import datetime as dt
from bs4 import BeautifulSoup

from src.common import checks
from src.structs.textpage import TextPage


class Miscellaneous(commands.Cog):

	@commands.command(name="lines")
	async def lines(self, ctx):
		""" Count the number of lines within the bot. """

		lines = 0

		for root, dirs, files in os.walk("./src/"):
			for f in files:
				if not f.endswith(".py"):
					continue

				path = os.path.join(root, f)

				with open(path, "r") as fh:
					lines += len(tuple(line for line in fh.read().splitlines() if line))

		await ctx.send(f"I am made up of **{lines:,}** lines of code.")

	@checks.nsfw_only()
	@commands.command(name="urban")
	async def urban_dict(self, ctx, *, term):
		""" Look up a term in urbandictionary.com """

		url = f"https://mashape-community-urban-dictionary.p.rapidapi.com/define?term={term}"

		headers = {
			'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
			'x-rapidapi-key': os.getenv("RAID_API_KEY")
		}

		async with httpx.AsyncClient() as client:
			r = await client.get(url, headers=headers)

		if r.status_code != httpx.codes.OK:
			return await ctx.send(f"I failed to lookup your query. Status Code: {r.status_code}")

		data = r.json()

		embed = ctx.bot.embed(title=term)

		for i, d in enumerate(data["list"][:5], start=1):
			def_ = d['definition'].strip().replace("[", "").replace("]", "").replace("\n", "")
			exa = d['example'].strip().replace("[", "").replace("]", "").replace("\n", "")

			value = f"{def_}\n\n{exa}"
			value = value[:1021] + "..." if len(value) > 1024 else value

			embed.add_field(name="Definition & Example", value=value, inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="whatis")
	async def what_is_this(self, ctx, *, word: str):
		""" Look for a word definition. """

		word = word.lower()

		async with httpx.AsyncClient() as client:
			r = await client.get(f"http://dictionary.reference.com/browse/{word.replace(' ', '_')}?s=t")

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

			embed = ctx.bot.embed(title=word)

			embed.add_field(name="Definition(s)", value=value)

			return await ctx.send(embed=embed)

		await ctx.send("I found no definitions or examples for your query.")

	@commands.command(name="invite")
	async def send_bot_invite(self, ctx):
		""" Bot invite link. """

		url = "https://discord.com/oauth2/authorize?client_id=666616515436478473&scope=bot&permissions=388168"

		await ctx.send(url)

	@commands.command(name="ping")
	async def ping(self, ctx):
		""" Check the bot latency. """

		await ctx.send(f"Pong! {round(ctx.bot.latency * 1000, 3)}ms")

	@commands.command(name="uptime")
	async def show_uptime(self, ctx):
		""" Display the bot uptime """

		embed = ctx.bot.embed(title="Bot Stats")

		embed.add_field(name="Bot", value=f"**Uptime: ** `{ctx.bot.uptime}`")

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

						page.add((cmd.name, dt.timedelta(seconds=int(retry_after))))

		if len(page.rows) == 0:
			page.set_footer("You have no active cooldowns")

		await ctx.send(page.get())


def setup(bot):
	bot.add_cog(Miscellaneous())
