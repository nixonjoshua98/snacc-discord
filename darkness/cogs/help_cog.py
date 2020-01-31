import discord
from discord.ext import commands

from darkness.common import checks
from darkness.common.constants import MEMBER_ROLE_NAME


class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.has_role(MEMBER_ROLE_NAME)
	@commands.check(checks.is_in_bot_channel)
	@commands.command(name="help")
	async def help(self, ctx):
		embed = discord.Embed(
			title="Help",
			description=f"``{self.bot.command_prefix}Help``",
			color=0xff8000,
		)

		embed.set_thumbnail(url=ctx.guild.icon_url)

		for cog_name in self.bot.cogs:
			cog = self.bot.get_cog(cog_name)

			coms = cog.get_commands()

			if len(coms) == 0 or cog == self:
				continue

			for com in coms:
				if com.hidden or not com.enabled:
					continue
					
				desc = "Description" if com.description == "" else com.description
				name = f"*{self.bot.command_prefix}{com.name}*"

				embed.add_field(name=name, value=desc, inline=False)

		embed.set_footer(text=self.bot.user.display_name)

		await ctx.send(embed=embed)