import discord


async def send_system_channel(guild, message):
    try:
        await guild.system_channel.send(message)

    except (AttributeError, discord.Forbidden, discord.HTTPException):
        """ Failed """
