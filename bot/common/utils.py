import os

from discord.ext.commands import CommandError


def config(f: str) -> str: return os.path.join(os.getcwd(), f)


def resource(f: str) -> str: return os.path.join(os.getcwd(), "bot", "resources", f)


def query(f: str) -> str: return os.path.join(os.getcwd(), "bot", "queries", f)


def get_tagged_role(cache, guild, tag):
    try:
        return guild.get_role(cache[guild.id].roles[tag])
    except (AttributeError, KeyError):

        raise CommandError(f"**Tagged role {tag} is invalid or has not been set**")


def get_tagged_channels(cache, guild, tag):
    try:
        return cache[guild.id].channels.get(tag, [])
    except (AttributeError, KeyError):
        return []
