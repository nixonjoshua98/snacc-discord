import enum
import discord


class LeaderboardType(enum.IntEnum):
	COIN = 0,
	PET = 1,
	ABO = 2


def create_leaderboard(author: discord.Member, lb_type: LeaderboardType):
	pass