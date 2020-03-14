import random
import discord

from discord.ext import commands

from src.common import checks

from src.common import FileReader
from src.common import leaderboard

from src.common import converters


class Bank(commands.Cog, name="bank"):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return await checks.requires_channel_tag("game")(ctx)

	@commands.command(name="balance", aliases=["bal"], help="Display your coin count")
	async def balance(self, ctx: commands.Context):
		with FileReader("coins.json") as coins_file:
			balance = coins_file.get_inner_key(str(ctx.author.id), "coins", 0)

		await ctx.send(f"**{ctx.author.display_name}** has a total of **{balance:,}** coins")

	@commands.cooldown(1, 60 * 15, commands.BucketType.user)
	@commands.command(name="free", aliases=["pickup"], help="Get free coins [15m]")
	async def free(self, ctx: commands.Context):
		amount = random.randint(15, 50)

		with FileReader("coins.json") as coins_file:
			balance = coins_file.get_inner_key(str(ctx.author.id), "coins", 0)

			coins_file.set_inner_key(str(ctx.author.id), "coins", balance + amount)

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")

	@commands.cooldown(1, 60 * 60 * 3, commands.BucketType.user)
	@checks.percent_chance_to_run(20, "failed to steal any coins")
	@commands.command(name="steal", help="Attempt to steal coins [3hrs]")
	async def steal_coins(self, ctx: commands.Context, target: converters.ValidUser()):
		with FileReader("coins.json") as file:
			author_coins = file.get_inner_key(str(ctx.author.id), "coins", 0)
			target_coins = file.get_inner_key(str(target.id), "coins", 0)

			max_coins = int(min(author_coins * 0.05, target_coins * 0.05, 1000))

			amount = random.randint(0, max(0, max_coins))

			file.set_inner_key(str(ctx.author.id), "coins", author_coins + amount)
			file.set_inner_key(str(target.id), "coins", author_coins - amount)

		msg = f"**{ctx.author.display_name}** stole **{amount:,}** coins from **{target.display_name}**"

		await ctx.send(msg)

	@commands.command(name="gift", help="Gift some coins")
	async def gift(self, ctx, target: converters.ValidUser(), amount: converters.GiftableCoins()):
		with FileReader("coins.json") as file:
			author_coins = file.get_inner_key(str(ctx.author.id), "coins", 0)
			target_coins = file.get_inner_key(str(target.id), "coins", 0)

			file.set_inner_key(str(ctx.author.id), "coins", author_coins - amount)
			file.set_inner_key(str(target.id), "coins", target_coins + amount)

		return await ctx.send(f"**{ctx.author.display_name}** gifted **{amount:,}** coins to **{target.display_name}**")

	@commands.is_owner()
	@commands.command(name="setcoins", hidden=True)
	async def set_coins(self, ctx, user: discord.Member, amount: int):
		with FileReader("coins.json") as file:
			file.set_inner_key(str(user.id), "coins", amount)

		await ctx.send(f"**{ctx.author.display_name}** done :thumbsup:")

	@commands.command(name="coinlb", aliases=["clb"], help="Show the coin leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		leaderboard_string = await leaderboard.create_leaderboard(ctx.author, leaderboard.Type.COIN)

		await ctx.send(leaderboard_string)