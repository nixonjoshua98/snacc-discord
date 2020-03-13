import discord
from discord.ext import commands
from discord.ext.commands import CommandError

from src.common import FileReader


class ValidUser(commands.MemberConverter):
	async def convert(self, ctx: commands.Context, argument: str) -> discord.Member:
		member = await super().convert(ctx, argument)

		if member.id == ctx.author.id or member.bot:
			raise CommandError(f"**{ctx.author.display_name}** :face_with_raised_eyebrow:")

		return member


class GiftableCoins(commands.Converter):
	async def convert(self, ctx: commands.Context, argument: str) -> int:
		amount = int(argument)

		with FileReader("coins.json") as file:
			coins = file.get_inner_key(str(ctx.author.id), "coins", 0)

		if amount <= 0 or amount > coins:
			raise CommandError(f"Nice try **{ctx.author.display_name}** :smile:")

		return amount
