from discord import Role, Forbidden, HTTPException

from discord.ext import commands

from src import menus
from src.common import SNACCMAN


class Snacc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return ctx.author.id == SNACCMAN

	@commands.command(name="dm")
	async def dm_role(self, ctx, role: Role, *, message: str):
		""" [Snacc] Send a DM to every server member with a certain role. """

		members = [member for member in role.members if not member.bot]

		if not await menus.confirm(ctx, f"Send a DM to **{len(members)}** member(s)?"):
			return await ctx.send("DM cancelled.")

		success, failed = [], []

		msg = await ctx.send("Sending DM...")

		txt = f"No members found with the `{role.name}` role."

		for i, member in enumerate(members):
			try:
				await member.send(message)

			except (Forbidden, HTTPException):
				failed.append(member)

			else:
				success.append(member)

			txt = f"Sucess: **{len(success)}/{len(members)}** | Failed: {', '.join(map(lambda m: str(m), failed))}"

			if i % 10 == 0:
				await msg.edit(content=txt)

		await msg.edit(content=txt)


def setup(bot):
	bot.add_cog(Snacc(bot))
