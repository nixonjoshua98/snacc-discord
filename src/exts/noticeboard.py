
from discord.ext import commands


class NoticeBoard(commands.Cog):

	@commands.command(name="log")
	async def log(self, ctx):
		""" Show your recent incoming attacks, steals etc. while uou was away. Logs are deleted after being viewed. """

		player = await ctx.bot.mongo.find_one("players", {"_id": ctx.author.id})

		embed = ctx.bot.embed(title=f"{str(ctx.author)}: Battle Log", description="Battle log is cleared after viewing")

		log = []

		for entry in player.get("log", []):
			event = entry.get('event')

			if event == "steal":
				value = f"{entry['thief']} stole ${entry['stolen_amount']:,}"

			elif event == "attack":
				value = f"{entry['attacker']} pillaged ${entry['stolen_amount']:,}"

				if units_lost := entry.get("units_lost"):
					value += f" and killed {units_lost}"

			else:
				continue

			log.append(value)

		# - Embed fields have a max length of 1024
		log = "\n".join(log)
		log = log[:1021] + "..." if len(log) >= 2014 else log

		embed.add_field(name="Log", value=log or "Empty")

		await ctx.send(embed=embed)

		# - Delete the log
		await ctx.bot.mongo.set_one("players", {"_id": ctx.author.id}, {"log": []})


def setup(bot):
	bot.add_cog(NoticeBoard())
