from discord.ext.commands import CommandError

from darkness.common.constants import (BOT_CHANNELS)


async def is_in_bot_channel(ctx):
	if ctx.channel.id not in BOT_CHANNELS:
		raise CommandError(f"**{ctx.author.display_name}**. Commands are disabled in this channel")

	return True