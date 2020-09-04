
from discord.ext import commands

from src import utils

from src.common.emoji import Emoji


class Inventory(commands.Cog):

	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.group(name="loot", invoke_without_command=True)
	async def show_loot(self, ctx):
		""" Display your loot.  """

		def check(r, u):
			return r.message.id == message.id and r.emoji == Emoji.MONEY_BAG and u.id == ctx.author.id

		# - Search the database and group items with the same name together
		loot = await ctx.bot.db["loot"].aggregate(
			[
				{"$match": {"user": ctx.author.id}},
				{
					"$group": {
						"_id": "$name",
						"ids": {"$addToSet": "$_id"},
						"name": {"$first": "$name"},
						"owned": {"$sum": 1},
						"total_value": {"$sum": "$value"}
					}
				},
				{"$project": {"_id": 0}}
			]
		).to_list(length=None)

		total_value = sum((item["total_value"] for item in loot))

		desc = []

		# - Create the loot listings
		for x, y in utils.grouper(loot, 2, None):
			s = f"{x['owned']:02d}x {x['name']: <13} "

			if y is not None:
				s += f"{y['owned']:02d}x {y['name']: <13}"

			desc.append(f"`{s}`")

		desc = "\n".join(desc)

		if loot and ctx.bot.has_permissions(ctx.channel, add_reactions=True):
			desc = f"React :moneybag: to sell. Total Value: **${total_value:,}**\n\n" + desc

		embed = ctx.bot.embed(title="Loot", description=desc, author=ctx.author)

		message = await ctx.send(embed=embed)

		if loot:
			await message.add_reaction(Emoji.MONEY_BAG)

			# - Wait for the money bag reaction from the targeted user
			react, user = await utils.wait_for_reaction(bot=ctx.bot, check=check, timeout=30.0)

			# - Reaction was given by the user? Sell the loot
			if react is not None and user is not None:
				all_ids = [_id for item in loot for _id in item["ids"]]

				await ctx.bot.db["loot"].delete_many({"user": ctx.author.id, "_id": {"$in": all_ids}})

				await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": total_value}}, upsert=True)

				await ctx.send(f"You sold your loot and gained **${total_value:,}**")

			# - Remove the reactions if we have permission
			if ctx.bot.has_permissions(ctx.channel, manage_messages=True):
				await message.clear_reactions()

	@commands.max_concurrency(1, commands.BucketType.user)
	@show_loot.command(name="sell")
	async def sell_loot(self, ctx):
		""" Sell all your loot. """

		# - Search the database and group items with the same name together
		loot = await ctx.bot.db["loot"].aggregate(
			[
				{"$match": {"user": ctx.author.id}},
				{
					"$group": {
						"_id": "$name",
						"ids": {"$addToSet": "$_id"},
						"name": {"$first": "$name"},
						"owned": {"$sum": 1},
						"total_value": {"$sum": "$value"}
					}
				},
				{"$project": {"_id": 0}}
			]
		).to_list(length=100)

		if not loot:
			return await ctx.send("You do not have any loot")

		total_value = sum((item["total_value"] for item in loot))

		all_ids = [_id for item in loot for _id in item["ids"]]

		await ctx.bot.db["loot"].delete_many({"user": ctx.author.id, "_id": {"$in": all_ids}})

		await ctx.bot.db["bank"].update_one({"_id": ctx.author.id}, {"$inc": {"usd": total_value}}, upsert=True)

		await ctx.send(f"You sold your loot and gained **${total_value:,}**")


def setup(bot):
	bot.add_cog(Inventory())
