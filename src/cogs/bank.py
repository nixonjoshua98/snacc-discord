import random

from discord.ext import commands
from src.common import checks
from src.common import backup

from src.structures import PlayerCoins


class Bank(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		backup.download_file("coins.json")

	async def cog_check(self, ctx):
		return await checks.in_bot_channel(ctx) and await checks.has_member_role(ctx) and commands.guild_only()

	@commands.command(name="balance", aliases=["bal"])
	async def balance(self, ctx):
		coins = PlayerCoins(ctx.author)

		await ctx.send(f"**{ctx.author.display_name}**, you have a total of **{coins.balance}** coins")

	@commands.is_owner()
	@commands.command(name="zero")
	async def zero_coins(self, ctx, _id: int):
		PlayerCoins(ctx.guild.get_member(_id)).zero()

		await ctx.send(f"**Done** :thumbsup:")

	@commands.cooldown(1, 60 * 60, commands.BucketType.user)
	@commands.command(name="coins", aliases=["c"])
	async def daily(self, ctx):
		coins = PlayerCoins(ctx.author)

		amount = random.randint(5, 25)

		coins.add(amount)

		await ctx.send(f"**{ctx.author.display_name}** gained **{amount}** coins!")