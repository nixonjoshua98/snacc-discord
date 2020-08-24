

import discord

from discord.ext import commands

from src.structs.confirm import Confirm

from src.common import DarknessServer, checks


class ABO(commands.Cog):

	@checks.snaccman_only()
	@checks.main_server_only()
	@commands.command(name="event")
	async def event(self, ctx):
		attachments = ctx.message.attachments

		# - Check a JSON file has been attached to the message
		"""		
		if not attachments:
			if not attachments[0].filename.lower().endswith("json"):
				return await ctx.send("A JSON file is required.")

		content = await attachments[0].read()
		"""

		top_performers = [(1, "Fanged"), (3, "Snaccman"), (4, "Lucaso7")]

		s = []

		role = ctx.guild.get_role(DarknessServer.EVENT_ROLE)

		for rank, username in top_performers:
			if rank == 1:
				continue

			print(rank, username)

	@checks.snaccman_only()
	@checks.main_server_only()
	@commands.command(name="champ")
	async def event_champion(self, ctx, user: discord.Member = None):
		async def give_event_winner_role(guild):
			role = guild.get_role(DarknessServer.EVENT_ROLE)

			for m in role.members:
				await m.remove_roles(role)

			if user is not None:
				await user.add_roles(role)

		event_role = discord.utils.get(ctx.guild.roles, id=DarknessServer.EVENT_ROLE)
		event_chnl = discord.utils.get(ctx.guild.channels, id=DarknessServer.FAME_CHANNEL)

		await give_event_winner_role(ctx.guild)

		await ctx.send(
			f"Congratulations **{str(user)}** on winning the event! "
			f"You have been given the {event_role.mention} role, "
			f"which allows you to send a few messages in {event_chnl.mention} "
			f"for everyone to see."
		)


def setup(bot):
	bot.add_cog(ABO(bot))
