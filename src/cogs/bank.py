import random
import discord

from discord.ext import commands
from src.common import checks
from src.common import backup

from src.structures import PlayerCoins


class Bank(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		backup.download_file("coins.json")

	async def cog_check(self, ctx):
		return await checks.in_bot_channel(ctx) and commands.guild_only()

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		coins = PlayerCoins(ctx.author)

		await ctx.send(f"**{ctx.author.display_name}** you have a total of **{coins.balance}** coins")

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="free")
	async def get_some_coins(self, ctx):
		coins = PlayerCoins(ctx.author)

		amount = random.randint(15, 35)

		coins.add(amount)

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.command(name="gift")
	async def gift(self, ctx, target_user: discord.Member, amount: int):
		user_coins, target_player = PlayerCoins(ctx.author), PlayerCoins(target_user)

		if amount < 0 or ctx.author.id == target_user.id:
			return await ctx.send(f"Nice try **{ctx.author.display_name}** :smile:")

		if user_coins.deduct(amount):
			target_player.add(amount)

			await ctx.send(f"**{ctx.author.display_name}** gifted **{target_user.display_name}** **{amount}** coins")

		else:
			await ctx.send(f"**{ctx.author.display_name}** failed to gift coins to {target_user.display_name}**")

	@commands.command(name="coinlb", aliases=["clb"])
	async def leaderboard(self, ctx):
		await ctx.send("This is totally a coin leaderboard")