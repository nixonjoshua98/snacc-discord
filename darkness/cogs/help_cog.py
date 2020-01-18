import discord
from discord.ext import commands


class Help(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
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

			# embed.add_field(name=cog_name, value="-", inline=False)

			for com in coms:
				desc = "Description" if com.description == "" else com.description
				name = f"*{self.bot.command_prefix}{com.name}*"

				embed.add_field(name=name, value=desc, inline=False)

		embed.set_footer(text=self.bot.user.display_name)

		await ctx.send(embed=embed)