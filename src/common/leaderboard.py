import enum
import discord

from src.common import FileReader


class Type(enum.IntEnum):
	COIN = 0,
	PET = 1,
	ABO = 2


LOOKUP_TABLE = {
	Type.COIN: {"file": "coins.json"}
}


async def create_leaderboard(author: discord.Member, lb_type: Type):
	lookup = LOOKUP_TABLE[lb_type]