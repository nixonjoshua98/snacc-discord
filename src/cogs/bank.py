import random
import discord

from discord.ext import commands

from src.common import checks
from src.common import myjson

from src.common import FileReader
from src.common import leaderboard


class Bank(commands.Cog, name="bank"):
	def __init__(self, bot):
		self.bot = bot

		myjson.download_file("coins.json")

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx)

	@commands.command(name="balance", aliases=["bal"], help="Display your coin count")
	async def balance(self, ctx: commands.Context):
		"""
		Send a message containing the member balance

		:param ctx: The message context
		:return:
		"""
		with FileReader("coins.json") as file:
			data = file.get(str(ctx.author.id), default_val=dict)

			author_bal = data.get("coins", 0)

		await ctx.send(f"**{ctx.author.display_name}** has a total of **{author_bal:,}** coins")

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="free", help="Get free coins [1hr Cooldown]")
	async def free(self, ctx: commands.Context):
		"""
		Gives the member a few coins, has a cooldown between uses.

		:param ctx: The message context
		:return:
		"""
		amount = random.randint(15, 35)

		with FileReader("coins.json") as file:
			data = file.get(str(ctx.author.id), default_val=dict)

			# Increment data
			data["coins"] = data.get("coins", 0) + amount

			# Set the new data
			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.command(name="gift", help="Gift some coins")
	async def gift(self, ctx, target_user: discord.Member, amount: int):
		"""
		Move coins from one member to another.

		:param ctx: The message context
		:param target_user: The user which the coins will be given too
		:param amount: The amount of coins to transfer to the target user
		:return:
		"""

		# Ignore
		if amount <= 0 or ctx.author.id == target_user.id:
			return await ctx.send(f"Nice try **{ctx.author.display_name}** :smile:")

		transaction_done = False

		with FileReader("coins.json") as file:
			author_data = file.get(str(ctx.author.id), default_val=dict)
			target_data = file.get(str(target_user.id), default_val=dict)

			# If the author has enough coins to gift
			if author_data.get("coins", 0) >= amount:
				transaction_done = True

				# Modify the coin counts
				author_data["coins"] = author_data.get("coins", 0) - amount
				target_data["coins"] = target_data.get("coins", 0) + amount

				# Set the new coin counts
				file.set(str(ctx.author.id), author_data)
				file.set(str(target_user.id), target_data)

		if transaction_done:
			return await ctx.send(f"**{ctx.author.display_name}** gifted **{amount:,}** coins to **{target_user.display_name}**")

		return await ctx.send(f"**{ctx.author.display_name}** failed to gift coins to **{target_user.display_name}**")

	@commands.is_owner()
	@commands.command(name="setcoins", hidden=True)
	async def set_coins(self, ctx, user: discord.Member, amount: int):
		"""
		Admin Command: Sets a users coin balance to a specified amount

		:param ctx: The message context
		:param user: The user whose coin balance will be set
		:param amount: The new coin balance
		:return:
		"""

		with FileReader("coins.json") as file:
			data = file.get(str(user.id), default_val=dict)

			data["coins"] = amount

			file.set(str(user.id), data)

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.command(name="coinlb", aliases=["clb"], help="Show the coin leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		"""
		Shows the coin leaderboard

		:param ctx: The message context
		:return:
		"""
		leaderboard_string = await leaderboard.create_leaderboard(ctx.author, leaderboard.Type.COIN)

		await ctx.send(leaderboard_string)