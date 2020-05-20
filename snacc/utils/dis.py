import discord


async def send_system_channel(guild, message):
    try:
        await guild.system_channel.send(message)

    except AttributeError:
        """ No guild system channel """

    except discord.Forbidden:
        """ Bot doesn't have access to the system channel """

    except discord.HTTPException:
        """ Failed for some other reason """
