import discord

from datetime import datetime


def create_embed(title: str, desc: str, thumbnail: str):
	embed = discord.Embed(title=title, description=desc, color=0xff8000)
	embed.set_thumbnail(url=thumbnail)
	embed.set_footer(text="Darkness")

	return embed


async def get_reaction_index(user: discord.Member, message: discord.Message):
	for i, reaction in enumerate(message.reactions):
		for reaction_user in await reaction.users().flatten():
			if reaction_user.id == user.id:
				return i


def pet_level_from_xp(data: dict) -> int:
	return 0


def abo_days_since_column(data: dict):
	days = (datetime.today() - datetime.strptime(data[0], "%d/%m/%Y %H:%M:%S")).days

	return f"{days} days ago" if days >= 7 else ""
