

import discord

from discord.ext import commands

from src.common import DarknessServer, checks


class ABOEvent(commands.Cog, name="ABO Event"):

	@checks.snaccman_only()
	@checks.main_server_only()
	@commands.command(name="champ")
	async def event_champion(self, ctx, user: discord.Member = None):
		async def give_event_winner_role():
			role = ctx.guild.get_role(DarknessServer.EVENT_ROLE)

			for m in role.members:
				await m.remove_roles(role)

			if user is not None:
				await user.add_roles(role)

		event_role = discord.utils.get(ctx.guild.roles, id=DarknessServer.EVENT_ROLE)
		event_chnl = discord.utils.get(ctx.guild.channels, id=DarknessServer.FAME_CHANNEL)

		await give_event_winner_role()

		await event_chnl.send(
			f"Congratulations **{user.mention}** on winning the event! "
			f"You have been given the {event_role.mention} role!"
		)

		await ctx.send(f"Done. Check {event_chnl.mention}")


def setup(bot):
	bot.add_cog(ABOEvent(bot))
