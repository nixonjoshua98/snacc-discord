import discord

from discord import Forbidden, HTTPException

from discord.ext import commands

from src.menus import YesNoMenu

from src.common import SNACCMAN


class Snacc(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx):
		return ctx.author.id == SNACCMAN

	@commands.command(name="dm")
	async def dm_role(self, ctx, role: discord.Role, *, message: str):
		""" Send a DM to every server member with a certain role. """

		async def confirm() -> bool:
			menu = YesNoMenu(ctx.bot, f"Send a DM to **{len(role.members)}** members?")

			await menu.send(ctx)

			return menu.get()

		if not await confirm():
			return await ctx.send("Command cancelled")

		success, failed = [], []

		msg = await ctx.send("Sending DM...")

		txt = f"No members found with the `{role.name}` role."

		for i, member in enumerate(role.members):
			try:
				await member.send(message)

			except (Forbidden, HTTPException):
				failed.append(member)

			else:
				success.append(member)

			txt = f"Sucess: **{len(success)}/{len(role.members)}** | Failed: {', '.join(map(lambda m: str(m), failed))}"

			if i % 10 == 0:
				await msg.edit(content=txt)

		await msg.edit(content=txt)


def setup(bot):
	bot.add_cog(Snacc(bot))
