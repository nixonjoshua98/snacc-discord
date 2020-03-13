import random
import discord

from discord.ext import commands

from src.common import checks

from src.common import FileReader
from src.common import leaderboard

from src.common.errors import InvalidTarget


class Bank(commands.Cog, name="bank"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.in_game_channel(ctx)

	@commands.command(name="balance", aliases=["bal"], help="Display your coin count")
	async def balance(self, ctx: commands.Context):
		"""
		Send a message containing the member balance

		:param ctx: The message context
		:return:
		"""
		with FileReader("coins.json") as file:
			data = file.get(str(ctx.author.id), default_val={})

			author_bal = data.get("coins", 0)

		await ctx.send(f"**{ctx.author.display_name}** has a total of **{author_bal:,}** coins")

	@commands.cooldown(1, 60 * 15, commands.BucketType.user)
	@commands.command(name="free", aliases=["pickup"], help="Get free coins [15m]")
	async def free(self, ctx: commands.Context):
		"""
		Gives the member a few coins, has a cooldown between uses.

		:param ctx: The message context
		:return:
		"""
		amount = random.randint(15, 35)

		with FileReader("coins.json") as file:
			data = file.get(str(ctx.author.id), default_val={})

			# Increment data
			data["coins"] = data.get("coins", 0) + amount

			# Set the new data
			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.cooldown(1, 60 * 60 * 2, commands.BucketType.user)
	@commands.command(name="steal", help="Attempt to steal coins [2hrs-help]")
	async def steal_coins(self, ctx: commands.Context, target: discord.Member):
		"""

		:param ctx:
		:param target:
		:return:
		"""
		if target.id == ctx.author.id or target.bot:
			raise InvalidTarget(f"**{ctx.author.display_name}** :face_with_raised_eyebrow:")

		if random.randint(0, 4) == 0:  # 20%
			with FileReader("coins.json") as file:
				author_data = file.get(str(ctx.author.id), default_val={})
				target_data = file.get(str(target.id), default_val={})

				# Limit the steal amount to X% of the lowest users coin balance
				steal_amount = int(min(target_data.get("coins", 10) * 0.05, author_data.get("coins", 10) * 0.05))
				steal_amount = random.randint(int(steal_amount * 0.5), steal_amount)

				if steal_amount > 0:
					author_data["coins"] = author_data.get("coins", 0) + steal_amount
					target_data["coins"] = target_data.get("coins", 0) - steal_amount

					return await ctx.send(f"**{ctx.author.display_name}** stole **{steal_amount:,}** coins from **{target.display_name}**")

		await ctx.send(f"**{ctx.author.display_name}** stole nothing from **{target.display_name}**")

	@commands.command(name="gift", help="Gift some coins")
	async def gift(self, ctx, target: discord.Member, amount: int):
		"""
		Move coins from one member to another.

		:param ctx: The message context
		:param target: The user which the coins will be given too
		:param amount: The amount of coins to transfer to the target user
		:return:
		"""

		# Ignore
		if amount <= 0 or ctx.author.id == target.id or target.bot:
			return await ctx.send(f"Nice try **{ctx.author.display_name}** :smile:")

		transaction_done = False

		with FileReader("coins.json") as file:
			author_data = file.get(str(ctx.author.id), default_val={})
			target_data = file.get(str(target.id), default_val={})

			# If the author has enough coins to gift
			if author_data.get("coins", 0) >= amount:
				transaction_done = True

				# Modify the coin counts
				author_data["coins"] = author_data.get("coins", 0) - amount
				target_data["coins"] = target_data.get("coins", 0) + amount

				# Set the new coin counts
				file.set(str(ctx.author.id), author_data)
				file.set(str(target.id), target_data)

		if transaction_done:
			return await ctx.send(f"**{ctx.author.display_name}** gifted **{amount:,}** coins to **{target.display_name}**")

		return await ctx.send(f"**{ctx.author.display_name}** failed to gift coins to **{target.display_name}**")

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
			data = file.get(str(user.id), default_val={})

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