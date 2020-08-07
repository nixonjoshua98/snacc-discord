import discord

from discord.ext import commands


class Server_701056373797945386(commands.Cog):
	@commands.command(name="apply")
	async def apply(self, ctx):
		if ctx.guild.id != 701056373797945386:
			return



def setup(bot):
	bot.add_cog(Server_701056373797945386())
