

from discord.ext import commands


def author_is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise commands.CommandError(f"**{ctx.author.display_name}**, you do not have access to this command")

	return True
