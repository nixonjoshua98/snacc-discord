
from discord.ext import commands


class InvalidCoinSide(commands.UserInputError):
    pass


class NotEnoughMoney(commands.CommandError):
    pass


class MemberRoleNotFound(commands.CommandError):
    pass


class InvalidRoleTag(commands.UserInputError):
    def __init__(self, *, tags):
        self.tags = tags
