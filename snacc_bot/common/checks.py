from discord.ext.commands import CommandError


async def is_server_owner(ctx):
	if ctx.author.id != ctx.guild.owner.id:
		raise CommandError(f":x: **{ctx.author.display_name}**, you do not have access to this command")

	return True
