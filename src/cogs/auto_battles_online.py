import discord

from discord.ext import commands
from discord.ext.commands import CommandError

from datetime import datetime

from src.common import FileReader
from src.common import checks
from src.common import functions

from src.structures import Leaderboard


class AutoBattlesOnline(commands.Cog, name="abo"):
	def __init__(self, bot):
		self.bot = bot

		self._leaderboard = Leaderboard(
			title="Trophy Leaderboard",
			file="game_stats.json",
			columns=[1, 2, 3],
			members_only=True,
			size=100,
			bot=self.bot,
			sort_func=lambda kv: kv[1][2]
		)

		self._leaderboard.update_column(1, "Lvl")
		self._leaderboard.update_column(2, "")
		self._leaderboard.update_column(3, "Updated", lambda data: AutoBattlesOnline.get_days_since_update(data))

	async def cog_check(self, ctx):
		return await checks.requires_channel_tag("abo")(ctx) and await checks.has_member_role(ctx)

	@staticmethod
	def get_days_since_update(data: dict):
		days = (datetime.today() - datetime.strptime(data[0], "%d/%m/%Y %H:%M:%S")).days

		return f"{days} days" if days >= 7 else ""

	@commands.command(name="me", help="Display your own stats")
	async def get_stats(self, ctx: commands.Context):
		with FileReader("game_stats.json") as file:
			stats = file.get(str(ctx.author.id), default_val=None)

			# Never set stats before
			if stats is None:
				msg = f"**{ctx.author.display_name}** you need to set your stats first :slight_smile:"

				raise CommandError(msg)

		embed = functions.create_embed(ctx.author.display_name, f"Auto Battles Online", ctx.author.avatar_url)

		for i, txt in enumerate(("Date Recorded", "Level", "Trophies")):
			embed.add_field(name=txt, value=stats[i], inline=False)

		await ctx.send(embed=embed)

	@commands.command(name="set", aliases=["s"], help="Set your game stats")
	async def set_stats(self, ctx, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today().strftime("%d/%m/%Y %H:%M:%S"), level, trophies]

			file.set(str(ctx.author.id), data)

		await ctx.send(f"**{ctx.author.display_name}** :thumbsup:")

	@commands.is_owner()
	@commands.command(name="setuser", hidden=True)
	async def set_user(self, ctx, user: discord.Member, level: int, trophies: int):
		with FileReader("game_stats.json") as file:
			data = [datetime.today().strftime("%d/%m/%Y %H:%M:%S"), level, trophies]

			file.set(str(user.id), data)

		await ctx.send(f"**{user.display_name}** :thumbsup:")

	@commands.command(name="alb", help="Display ABO trophy leaderboard")
	async def leaderboard(self, ctx: commands.Context):
		leaderboard_string = await self._leaderboard.create(ctx.author)

		return await ctx.send(leaderboard_string)