import os

from discord.ext import commands


def config(f: str) -> str: return os.path.join(os.getcwd(), f)


def resource(f: str) -> str: return os.path.join(os.getcwd(), "bot", "resources", f)


def get_tagged_role(cache, server, tag, *, ignore_exception: bool = False):
    """
    :param cache: The server config cache stored on the bot object
    :param server: Discord server
    :param tag: The tag of the role wanted (e.g. leader or member)
    :param ignore_exception: Decide to ignore the raised error, and instead return None
    :return: Return the discord role object (or None if <ignore_exception>
    :raise CommandError: Raises if the role assoiated with the tag is not valid or set.
    """
    try:
        return server.get_role(cache[server.id].roles[tag])
    except (AttributeError, KeyError):
        if not ignore_exception:
            raise commands.CommandError(f"**Tagged role {tag} is invalid or has not been set**")


def get_tagged_channels(cache, server, tag):
    """
    :param cache: The server config cache stored on the bot object
    :param server: Discord server
    :param tag: Tag of the channels we are looking for
    :return: List of channels with the tag, or an empty list if not found
    """
    try:
        return cache[server.id].channels.get(tag, [])
    except (AttributeError, KeyError):
        return []
