import discord


def create_embed(title: str, desc: str, thumbnail: str):
	embed = discord.Embed(title=title, description=desc, color=0xff8000)

	embed.set_thumbnail(url=thumbnail)

	embed.set_footer(text="Auto Battles Online [Snaccman]")

	return embed


async def get_reaction_index(user: discord.Member, message: discord.Message):
	for i, reaction in enumerate(message.reactions):
		for reaction_user in await reaction.users().flatten():
			if reaction_user.id == user.id:
				return i
