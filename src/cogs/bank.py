import random
import discord

from discord.ext import commands
from src.common import checks
from src.common import myjson

from src.common import FileReader


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
			balance = file.get(str(ctx.author.id), default_val=0)

		await ctx.send(f"**{ctx.author.display_name}** has a total of **{balance:,}** coins")

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
			file.increment(str(ctx.author.id), amount, default_val=0)

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
		if amount <= 0 or ctx.author.id == target_user.id:
			return await ctx.send(f"Nice try **{ctx.author.display_name}** :smile:")

		transaction_done = False

		with FileReader("coins.json") as file:
			from_user = file.get(str(ctx.author.id), default_val=0)

			if from_user >= amount:
				transaction_done = True
				file.decrement(str(ctx.author.id), amount, default_val=0)
				file.increment(str(target_user.id), amount, default_val=0)

		if transaction_done:
			await ctx.send(f"**{ctx.author.display_name}** gifted **{amount:,}** coins to **{target_user.display_name}**")

		else:
			await ctx.send(f"**{ctx.author.display_name}** failed to gift coins to **{target_user.display_name}**")

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
			file.set(str(user.id), value=amount)

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.command(name="coinlb", aliases=["clb"], help="Show the coin leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		def get_user_rank(val) -> int:
			try:
				return data.index(val) + 1
			except IndexError:
				return len(data)
		"""
		Shows the coin leaderboard

		:param ctx: The message context
		:return:
		"""
		with FileReader("coins.json") as file:
			data = sorted(file.data().items(), key=lambda k: k[1], reverse=True)

			user_data = (str(ctx.author.id), file.get(str(ctx.author.id), default_val=0))

		leaderboard_size = 10
		top_players = data[0: leaderboard_size]
		max_username_length = 20
		user_rank = get_user_rank(user_data)
		row_length = 1

		msg = f"```c++\nCoin Leaderboard\n\n    Username{' ' * (max_username_length - 7)}Coins"

		for rank, (user_id, user_balance) in enumerate(top_players, start=1):
			user = ctx.guild.get_member(int(user_id))
			username = user.display_name[0:max_username_length] if user else "> User Left <"
			row = f"\n#{rank:02d} {username}{' ' * (max_username_length - len(username)) + ' '}{user_balance:05d}"

			msg += row
			row_length = max(row_length, len(row))
			rank += 1

		if user_rank > leaderboard_size:
			username = ctx.author.display_name[0:max_username_length]
			row = f"\n#{user_rank:02d} {username}{' ' * (max_username_length - len(username)) + ' '}{user_data[1]:05d}"
			msg += "\n" + "-" * row_length + "\n" + row

		msg += "```"

		await ctx.send(msg)