import discord


async def send(dest, content, embed=None):
	try:
		await dest.send(content=content, embed=embed)

	except (discord.HTTPException, discord.Forbidden):
		return False

	return True
