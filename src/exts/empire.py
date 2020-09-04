import random

import datetime as dt

from pymongo import UpdateOne, UpdateMany

from discord.ext import tasks, commands

from src import utils
from src.common import checks
from src.common.converters import AnyoneWithEmpire
from src.common.population import Workers, Military

from src.structs.textleaderboard import TextLeaderboard

MAX_HOURS_OFFLINE = 8


class Empire(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_startup")
	async def on_startup(self):
		print("Starting loop: Income")

		self.income_loop.start()

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

		row = dict(_id=ctx.author.id, name=empire_name, last_income=now, last_attack=now)

		await ctx.bot.db["empires"].insert_one(row)

		await ctx.send(f"Your empire has been established! You can rename your empire using `{ctx.prefix}rename`")

		await self.show_tutorial(ctx)

	@checks.has_empire()
	@commands.command(name="rename")
	async def rename_empire(self, ctx, *, name):
		""" Rename your established empire. """

		await self.bot.db["empires"].update_one({"_id": ctx.author.id}, {"name": name})

		await ctx.send(f"Your empire has been renamed to `{name}`")

	@checks.has_empire()
	@commands.command(name="empire", aliases=["e"])
	async def show_empire(self, ctx, target: AnyoneWithEmpire() = None):
		""" View information about any empire. """

		target = ctx.author if target is None else target

		empire = await ctx.bot.db["empires"].find_one({"_id": target.id}) or dict()

		# - Calculate the values used in the Embed message
		hourly_income = Workers.get_total_hourly_income(empire)
		hourly_upkeep = Military.get_total_hourly_upkeep(empire)

		total_power = Military.calc_total_power(empire)

		# - Create the Embed message which will be sent back to Discord
		embed = ctx.bot.embed(
			title=empire.get('name', target.display_name),
			thumbnail=target.avatar_url,
			author=target
		)

		embed.add_field(name="General", value=f"**Power Rating:** `{total_power:,}`")

		embed.add_field(name="Finances", value=f"**Income:** `${hourly_income:,}`\n**Upkeep:** `${hourly_upkeep:,}`")

		await ctx.send(embed=embed)

	@commands.command(name="power", aliases=["empires"])
	async def power_leaderboard(self, ctx):
		""" Display the most powerful empires. """

		async def query():
			empires = await ctx.bot.db["empires"].find({}).to_list(length=100)

			for i, row in enumerate(empires):
				empires[i] = dict(_id=row["_id"], power=Military.calc_total_power(row))

			empires.sort(key=lambda ele: ele["power"], reverse=True)

			return empires

		await TextLeaderboard(title="Top Empires", columns=["power"], order_by="power", query_func=query).send(ctx)

	@checks.has_empire()
	@commands.cooldown(1, 60 * 90, commands.BucketType.user)
	@commands.command(name="empireevent", aliases=["ee"])
	async def empire_event(self, ctx):
		""" Trigger an empire event. """

		options = (loot_event, stolen_event, assassinated_event, recruit_unit)
		weights = (85, 10, 10, 25)

		chosen_events = random.choices(options, weights=weights, k=1)

		for event in chosen_events:
			await event(ctx)

	@tasks.loop(hours=1.0)
	async def income_loop(self):
		""" Background income & upkeep loop. """

		empires = await self.bot.db["empires"].find({}).to_list(length=None)

		requests = []

		for empire in empires:
			now = dt.datetime.utcnow()

			player_row = await self.bot.db["players"].find_one({"_id": empire["_id"]}) or dict()

			# - Set the last_income field which is used to calculate the income rate from the delta time
			await self.bot.db["empires"].update_one({"_id": empire["_id"]}, {"$set": {"last_income": now}})

			# - No login? No income
			if (last_login := player_row.get("last_login")) is None:
				continue

			last_income = empire.get("last_income", now)

			hours_since_login = (now - last_login).total_seconds() / 3600

			# - User must have logged in the past 8 hours in order to get passive income
			if hours_since_login >= MAX_HOURS_OFFLINE:
				continue

			# - Total number of hours we need to credit the empire's bank
			hours = (now - last_income).total_seconds() / 3600

			income = int(utils.net_income(empire) * hours)

			requests.append(UpdateOne({"_id": empire["_id"]}, {"$inc": {"usd": income}}, upsert=True))

		requests.append(UpdateMany({"usd": {"$lt": 0}}, {"$set": {"usd": 0}}))

		await self.bot.db["bank"].bulk_write(requests)


async def assassinated_event(ctx):
	""" Single unit is killed. """

	empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

	units = empire.get("units", dict())

	# - List of all military units which have an owned amount greater than 0
	units_owned = [u for u in Military.units if units.get(u.key, dict()).get("owned", 0) > 0]

	if len(units_owned) > 0:

		# - Select the most expensive unit to kill
		unit_killed = max(units_owned, key=lambda u: u.calc_price(units.get(u.key, dict()).get("owned", 0), 1))

		await ctx.bot.db["empires"].update_one(
			{"_id": ctx.author.id},
			{"$inc": {f"units.{unit_killed.key}.owned": -1}},
			upsert=True
		)

		await ctx.send(f"One of your **{unit_killed.display_name}** was assassinated.")

	else:
		# - The user has no units so we send a generic message and do not do anything
		await ctx.send("An assassin from a rival empire was found dead in your empire")


async def stolen_event(ctx):
	""" Empire was stolen from event. """

	empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

	income = utils.net_income(empire)

	money_stolen = random.randint(max(250, income // 2), max(1_000, income))

	await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": -money_stolen}}, upsert=True)

	s = f"${money_stolen:,}" if money_stolen > 0 else "nothing"

	await ctx.send(f"A thief broke into your empire and stole **{s}**")


async def loot_event(ctx):
	""" Empire finds loot event. """

	empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

	income = utils.net_income(empire)

	name = utils.get_random_name()
	value = random.randint(max(500, income // 2), max(1_000, int(income * 0.75)))

	await ctx.bot.db["loot"].insert_one({"user": ctx.author.id, "name": name, "value": value})

	await ctx.send(f"You found **- {name} -** while out adventuring.")


async def recruit_unit(ctx):
	""" Empire gains a unit or gains money. """

	empire = await ctx.bot.db["empires"].find_one({"_id": ctx.author.id})

	units = empire.get("units", dict())

	# - Get available units
	avail_units = []
	for unit in Military.units:
		unit_entry = units.get(unit.key, dict())

		if unit_entry.get("owned", 0) > 0:
			avail_units.append(unit)

	if avail_units:
		unit_recruited = min(avail_units, key=lambda u: u.calc_price(units.get(u.key, dict()).get("owned", 0), 1))

		await ctx.bot.db["empires"].update_one(
			{"_id": ctx.author.id},
			{"$inc": {f"units.{unit_recruited.key}.owned": 1}},
			upsert=True
		)

		await ctx.send(f"You recruited a rogue **{unit_recruited.display_name}!**")

	else:
		await loot_event(ctx)


def setup(bot):
	bot.add_cog(Empire(bot))
