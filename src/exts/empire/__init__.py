

import random
import discord

import datetime as dt

from discord.ext import tasks, commands

from src import inputs, utils
from src.common import DarknessServer, checks
from src.common.converters import AnyoneWithEmpire

from src.data import Military, Workers

from src.exts.empire import events


MAX_HOURS_OFFLINE = 8


class Empire(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		print("Starting loop: Income")

		self.income_loop.start()

	async def cog_before_invoke(self, ctx):
		if ctx.guild.id == DarknessServer.ID:
			await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, id=DarknessServer.EMPIRE_ROLE))

	async def cog_after_invoke(self, ctx):
		await ctx.bot.mongo.set_one("empires", {"_id": ctx.author.id}, {"last_login": dt.datetime.utcnow()})

	@commands.command(name="tutorial")
	async def show_tutorial(self, ctx):
		""" Show the tutorial embed. """

		embed = ctx.bot.embed(
			title="Empire Tutorial",
			description=(
				f"Empire is a idle PvP/PvE gamemode which involves hiring units to generate passive income as well as "
				f"hiring military units to attack other users, complete quests, steal from others users. More features "
				f"are constantly being added. You can view your empire using **{ctx.prefix}e**."
			)
		)

		embed.add_field(
			name="Getting started",
			value=(
				f"You can claim your daily reward every 24 hours by doing **{ctx.prefix}daily**. It is also a good "
				f"idea to hire at least 1 thief military unit, which is used to **{ctx.prefix}steal** from other "
				f"players. You should focus more on workers, than military at the start of your game."
			),
			inline=False
		)

		embed.add_field(
			name="Units (Workers)",
			value=(
				f"Worker units generate passive income which is automatically added to your bank account each hour. "
				f"Hourly income can also be collected manually using **{ctx.prefix}collect**."
			),
			inline=False
		)

		embed.add_field(
			name="Units (Military)",
			value=(
				f"Military units, unlike Workers, need to be paid an upkeep every hour but they can be used to attack "
				f"and steal from other players, complete quests, and more to come. You can view the most powerful "
				f"empires using **{ctx.prefix}power**."
			),
			inline=False
		)

		embed.add_field(
			name="Support Server",
			value=(
				f"The support server https://discord.gg/QExQuvE offers daily giveaways, support (obviously), and "
				f"soon-to-be bosses and much more."
			),
			inline=False
		)

		embed.add_field(
			name="Final Notes",
			value=(
				f"I am filled with lots of things to do, but this tutorial is supposed to be short. "
				f"You can view all my commands using the **{ctx.prefix}help** command."
			),
			inline=False
		)

		await ctx.send(embed=embed)

	@checks.no_empire()
	@commands.command(name="create")
	@commands.max_concurrency(1, commands.BucketType.user)
	async def create_empire(self, ctx, *, empire_name: str):
		""" Establish an empire under your name. """

		now = dt.datetime.utcnow()

		row = dict(name=empire_name, last_login=now, last_income=now)

		await ctx.bot.mongo.set_one("empires", {"_id": ctx.author.id}, row)

		await ctx.send(f"Your empire has been established! You can rename your empire using `{ctx.prefix}rename`")

		await self.show_tutorial(ctx)

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="empire", aliases=["e"])
	async def show_empire(self, ctx, target: AnyoneWithEmpire() = None):
		""" View information about any empire. """

		target = ctx.author if target is None else target

		empire = await ctx.bot.mongo.find_one("empires", {"_id": target.id})
		units = await ctx.bot.mongo.find_one("units", {"_id": target.id})
		levels = await ctx.bot.mongo.find_one("levels", {"_id": target.id})

		# - Calculate the values used in the Embed message
		hourly_income = Workers.get_total_hourly_income(units, levels)
		hourly_upkeep = Military.get_total_hourly_upkeep(units, levels)

		total_power = Military.get_total_power(units)

		name = empire.get('name', target.display_name)

		# - Create the Embed message which will be sent back to Discord
		embed = ctx.bot.embed(title=f"{str(target)}: {name}", thumbnail=target.avatar_url)

		embed.add_field(name="General", value=f"**Power Rating:** `{total_power:,}`")

		embed.add_field(name="Finances", value=f"**Income:** `${hourly_income:,}`\n**Upkeep:** `${hourly_upkeep:,}`")

		await ctx.send(embed=embed)

	@checks.has_empire()
	@commands.command(name="rename")
	async def rename_empire(self, ctx, *, new_name):
		""" Rename your established empire. """

		await self.bot.mongo.set_one("empires", {"_id": ctx.author.id}, {"name": new_name})

		await ctx.send(f"Your empire has been renamed to `{new_name}`")

	@checks.has_empire()
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="collect")
	async def collect_income(self, ctx):
		""" Collect your hourly income. """

		now = dt.datetime.utcnow()

		# - Load data from database
		empire = await ctx.bot.mongo.find_one("empires", {"_id": ctx.author.id})
		levels = await ctx.bot.mongo.find_one("levels", {"_id": ctx.author.id})
		units = await ctx.bot.mongo.find_one("units", {"_id": ctx.author.id})

		# - Calculate passive income
		if empire.get("last_income") is not None:
			hours = min(MAX_HOURS_OFFLINE, (now - empire["last_income"]).total_seconds() / 3600)

			hourly_income = Workers.get_total_hourly_income(units, levels)
			hourly_upkeep = Military.get_total_hourly_upkeep(units, levels)

			money_change = int((hourly_income + hourly_upkeep) * hours)

			# - Update database
			await ctx.bot.mongo.increment_one("bank", {"_id": empire["_id"]}, {"usd": money_change})

			await ctx.send(f"You received **${money_change:,}**")

		else:
			await ctx.send("Failed to collect. Try again")

		await ctx.bot.mongo.set_one("empires", {"_id": empire["_id"]}, {"last_income": now})

	@checks.has_empire()
	@commands.cooldown(1, 60 * 90, commands.BucketType.user)
	@commands.command(name="empireevent", aliases=["ee"])
	async def empire_event(self, ctx):
		""" Trigger an empire event. """

		options = (events.loot_event, events.stolen_event, events.assassinated_event, events.recruit_unit)
		weights = (85, 10, 10, 25)

		chosen_events = random.choices(options, weights=weights, k=1)

		for event in chosen_events:
			await event(ctx)

	@commands.cooldown(1, 15, commands.BucketType.guild)
	@commands.command(name="power", aliases=["empires"])
	async def power_leaderboard(self, ctx):
		""" Display the most powerful empires. """

		async def query():
			empires = await ctx.bot.mongo.find("units").to_list(length=100)

			for i, row in enumerate(empires):
				empires[i] = dict(**row, __power__=Military.get_total_power(row))

			empires.sort(key=lambda ele: ele["__power__"], reverse=True)

			return empires

		await inputs.show_leaderboard(
			ctx,
			"Most Powerful Empires",
			columns=["__power__"],
			order_by="__power__",
			query_func=query,
			headers=["Power"]
		)

	@tasks.loop(hours=1.0)
	async def income_loop(self):
		""" Background income & upkeep loop. """

		empires = await self.bot.mongo.find("empires").to_list(length=None)

		for empire in empires:
			now = dt.datetime.utcnow()

			# - Set the last_income field which is used to calculate the income rate from the delta time
			await self.bot.mongo.set_one("empires", {"_id": empire["_id"]}, {"last_income": now})

			last_login = empire.get("last_login", now)
			last_income = empire.get("last_income", now)

			hours_since_login = (now - last_login).total_seconds() / 3600

			# - User must have logged in the past 8 hours in order to get passive income
			if hours_since_login >= MAX_HOURS_OFFLINE:
				continue

			# - Query the database
			bank = await self.bot.mongo.find_one("bank", {"_id": empire["_id"]})
			units = await self.bot.mongo.find_one("units", {"_id": empire["_id"]})
			levels = await self.bot.mongo.find_one("levels", {"_id": empire["_id"]})

			# - Total number of hours we need to credit the empire's bank
			hours = (now - last_income).total_seconds() / 3600

			hourly_income = max(0, int(utils.net_income(units, levels) * hours))

			if hourly_income > 0 and (bank.get("usd", 0) >= 250_000 or bank.get("btc", 0) >= 250):
				hourly_income = int(hourly_income * 0.4)

			if hourly_income > 0:
				await self.bot.mongo.increment_one("bank", {"_id": empire["_id"]}, {"usd": hourly_income})

			elif hourly_income < 0:
				await self.bot.mongo.decrement_one("bank", {"_id": empire["_id"]}, {"usd": abs(hourly_income)})


def setup(bot):
	bot.add_cog(Empire(bot))
