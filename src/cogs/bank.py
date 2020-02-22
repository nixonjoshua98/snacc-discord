import random
import discord

from discord.ext import commands
from src.common import checks
from src.common import backup
from src.common import data_reader

from src.structures import PlayerCoins


class Bank(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		backup.download_file("coins.json")

	async def cog_check(self, ctx):
		return await checks.in_game_room(ctx) and commands.guild_only()

	@commands.command(name="balance", aliases=["bal"], help="Display your coin count")
	async def balance(self, ctx):
		coins = PlayerCoins(ctx.author)

		await ctx.send(f"**{ctx.author.display_name}** you have a total of **{coins.balance}** coins")

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="free", help="Get some free coins")
	async def free(self, ctx):
		coins = PlayerCoins(ctx.author)

		amount = random.randint(15, 35)

		coins.add(amount)

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.command(name="gift", help="Gift some coins to someone else")
	async def gift(self, ctx, target_user: discord.Member, amount: int):
		user_coins, target_player = PlayerCoins(ctx.author), PlayerCoins(target_user)

		if amount <= 0 or ctx.author.id == target_user.id:
			return await ctx.send(f"Nice try **{ctx.author.display_name}** :smile:")

		if user_coins.deduct(amount):
			target_player.add(amount)

			await ctx.send(f"**{ctx.author.display_name}** gifted **{target_user.display_name}** **{amount}** coins")

		else:
			await ctx.send(f"**{ctx.author.display_name}** failed to gift coins to {target_user.display_name}**")

	@commands.is_owner()
	@commands.command(name="setcoins", hidden=True)
	async def set_coins(self, ctx, user: discord.Member, amount: int):
		PlayerCoins(user).set(amount)

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.cooldown(1, 15, commands.BucketType.user)
	@commands.command(name="coinlb", aliases=["clb"], help="Show the coin leaderboard")
	async def leaderboard(self, ctx):
		data = sorted(data_reader.read_json("coins.json").items(), key=lambda k: k[1], reverse=True)

		msg, rank = "```Coin Leaderboard\n\n    Username        Coins", 1

		for _id, amount in data:
			user = ctx.guild.get_member(int(_id))

			if user and amount > 0:
				username_gap = " " * (15 - len(user.display_name)) + " "
				msg += f"\n#{rank:02d} {user.display_name[0:15]}{username_gap}{amount:05d}"
				rank += 1

		msg += "```"

		await ctx.send(msg)