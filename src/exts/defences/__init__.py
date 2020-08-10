import os
import discord

from discord.ext import commands

from . import city

from .city import Buildings

from src.common import checks
from src.common.models import EmpireM


class Defences(commands.Cog):

	@checks.has_empire()
	@commands.group(name="defences", aliases=["d"])
	async def show_city(self, ctx):
		""" Display your Empire defences. """

		buildings = [
			Buildings.WALL, Buildings.WALL, 	Buildings.WALL, 	Buildings.WALL, 	Buildings.WALL,
			Buildings.WALL, Buildings.WATER, 	Buildings.WATER, 	Buildings.WATER, 	Buildings.WALL,
			Buildings.WALL, Buildings.WATER, 	Buildings.CASTLE, 	Buildings.WATER, 	Buildings.WALL,
			Buildings.WALL, Buildings.WATER, 	Buildings.WATER, 	Buildings.WATER, 	Buildings.WALL,
			Buildings.WALL, Buildings.WALL, 	Buildings.WALL, 	Buildings.WALL, 	Buildings.WALL,
		]

		empire = await EmpireM.fetchrow(ctx.bot.pool, ctx.author.id)

		image = city.build_city_image(buildings)

		fp = f"city_{ctx.author.id}.png"

		image.save(fp)

		embed = ctx.bot.embed(title=empire['name'])

		file = discord.File(fp, filename=fp)

		embed.set_image(url=f"attachment://{fp}")

		await ctx.send(file=file, embed=embed)

		os.remove(fp)


def setup(bot):
	bot.add_cog(Defences())
