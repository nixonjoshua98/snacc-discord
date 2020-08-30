
from discord.ext import commands

from src import utils

from src.common.emoji import Emoji


class Inventory(commands.Cog):

	@commands.bot_has_permissions(add_reactions=True)
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.command(name="loot")
	async def show_loot(self, ctx):
		""" Display your loot, with the option of selling it all. """

		def check(r, u):
			return r.message.id == message.id and r.emoji == Emoji.MONEY_BAG and u.id == ctx.author.id

		# - Search the database and group items with the same name together
		loot = await ctx.bot.mongo.snacc["loot"].aggregate(
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

		total_value = sum((item["total_value"] for item in loot))

		# - Create the embed description
		desc = [f"`{item['owned']:02d}x` `{item['name']}`" for item in loot]
		desc = f"React :moneybag: to sell. Total Value: **${total_value:,}**\n\n" + "\n".join(desc)

		embed = ctx.bot.embed(title="Loot", description=desc)

		message = await ctx.send(embed=embed)

		if loot:
			await message.add_reaction(Emoji.MONEY_BAG)

			# - Wait for the money bag reaction from the targeted user
			react, user = await utils.wait_for_reaction(bot=ctx.bot, check=check, timeout=60.0)

			# - Reaction was given by the user? Sell the loot
			if react is not None and user is not None:
				all_ids = [_id for item in loot for _id in item["ids"]]

				await ctx.bot.mongo.snacc["loot"].delete_many({"user": ctx.author.id, "_id": {"$in": all_ids}})

				await ctx.bot.mongo.snacc["bank"].update_one({"user": "ctx.author.id"}, {"$inc": {"usd": total_value}})

				await ctx.send(f"You sold your loot and gained **${total_value:,}**")

			# - Remove the reactions if we have permission
			if ctx.bot.has_permission(ctx.channel, manage_messages=True):
				await message.clear_reactions()


def setup(bot):
	bot.add_cog(Inventory())
