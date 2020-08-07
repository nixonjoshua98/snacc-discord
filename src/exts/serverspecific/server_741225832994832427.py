import discord

from discord.ext import commands


OPEN_MOD_CHANNELS = (741271430758531082, 741279452876636227)


class Server_741225832994832427(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener(name="on_message")
	async def on_message(self, message):
		if (
				message.guild.id != 741225832994832427 or
				message.author.bot or
				message.channel.id in OPEN_MOD_CHANNELS or
				message.channel.category is None
		):
			return

		cat = message.channel.category.name.upper()

		if cat in ("SERVER ADVERTISMENTS", "BOT ADVERTISMENTS"):
			embed = self.bot.embed(title="Reminder")

			rules = discord.utils.get(message.guild.channels, id=741278149978882058)
			booster = discord.utils.get(message.guild.channels, id=741278149978882058)

			embed.description = (
				f"• Before posting be sure to read {rules.mention} to have your ads not deleted\n"
				f"• Boost to gain special perks, read more in {booster.mention}\n"
				f"• Once you leave, all of your messages will be deleted"
			)

			await message.channel.send(embed=embed)

	@commands.Cog.listener(name="on_member_remove")
	async def on_member_remove(self, member):
		if member.guild.id != 741225832994832427:
			return

		for cat in member.guild.categories:
			if cat.name.upper() in ("SERVER ADVERTISMENTS", "BOT ADVERTISMENTS"):
				for chnl in cat.channels:
					async for msg in chnl.history(limit=100):
						if msg.author.id == member.id:
							try:
								await msg.delete()
							except (discord.HTTPException, discord.Forbidden):
								""" Failed """


def setup(bot):
	bot.add_cog(Server_741225832994832427(bot))
