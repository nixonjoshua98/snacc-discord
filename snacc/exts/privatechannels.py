import itertools
import os
import discord
import secrets

from typing import Optional

from discord.ext import commands, tasks

from datetime import datetime, timedelta

from snacc.common.converters import NormalUser
from snacc.common.queries import PrivateChannelsSQL


class PrivateChannels(commands.Cog, name="Private Channels"):
	""" All commands are sub commands. E.g `!pc add User#1234` """
	def __init__(self, bot):
		self.bot = bot

		if not os.getenv("DEBUG", False):
			self.channel_manager.start()

	@staticmethod
	async def create_category(guild):
		for cat in guild.categories:
			if cat.name.upper() == "PRIVATE":
				return cat

		return await guild.create_category("Private")

	@tasks.loop(minutes=15.0)
	async def channel_manager(self):
		results = await self.bot.pool.fetch(PrivateChannelsSQL.SELECT_EXPIRING_CHANNELS)

		def key_func(ele): return ele["server_id"]

		now = datetime.utcnow()

		for server_id, rows in itertools.groupby(sorted(results, key=key_func), key=key_func):
			server = self.bot.get_guild(int(server_id))

			for row in rows:
				if server is None:
					await self.bot.pool.execute(PrivateChannelsSQL.DELETE_ROW, row["server_id"], row["channel_id"])
					continue

				channel = server.get_channel(int(row["channel_id"]))

				hours_since_created = (now - channel.created_at).total_seconds() / 3600

				if hours_since_created > row["lifetime"]:
					await self.bot.pool.execute(PrivateChannelsSQL.DELETE_ROW, row["server_id"], row["channel_id"])

					await channel.delete()

				elif abs(hours_since_created - row["lifetime"]) <= 1.0:
					expire_date = channel.created_at + timedelta(hours=row["lifetime"])

					cd = timedelta(seconds=int(abs((expire_date - now).total_seconds())))

					await channel.send(f"Channel is set to expire in `{cd}`.")

	@commands.cooldown(1, 60 * 30, commands.BucketType.member)
	@commands.bot_has_permissions(manage_channels=True)
	@commands.group(name="private", aliases=["pc"], invoke_without_command=True)
	async def private_channel(self, ctx, name: Optional[str] = None):
		""" Create a private channel. """

		overwrites = {
			ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
			ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
		}

		name = name if name is not None else secrets.token_urlsafe(8).lower()

		category = await self.create_category(ctx.guild)

		channel = await ctx.guild.create_text_channel(name, overwrites=overwrites, category=category)

		await ctx.bot.pool.execute(
			PrivateChannelsSQL.INSERT_CHANNEL,
			str(ctx.guild.id), str(channel.id), str(ctx.author.id), 6.0
		)

		await ctx.send(f"Channel with name **{channel.name}** has been created!")

		await channel.send(
			f"Invite members to this channel by using `{ctx.prefix}pc invite <username>`.\n"
			f"This channel will be deleted in **6** hours but can be extended using `{ctx.prefix}pc extend`"
		)

	@commands.bot_has_permissions(manage_roles=True)
	@private_channel.command(name="add")
	async def add_member(self, ctx, user: NormalUser()):
		""" [Sub Command] Add a member to the current private channel. """

		await ctx.channel.set_permissions(user, read_messages=True)

		await ctx.send(f"{user.mention} has been added to this channel.")

	@commands.cooldown(1, 60 * 60, commands.BucketType.channel)
	@private_channel.command(name="extend")
	async def extend_lifetime(self, ctx):
		""" [Sub Command] Extend the lifetime of theprivate channel. """

		row = await ctx.bot.pool.fetchrow(PrivateChannelsSQL.SELECT_CHANNEL, str(ctx.guild.id), str(ctx.channel.id))

		if row is None:
			return await ctx.send(f"{ctx.channel.mention} is not a private channel created by me.")

		# Author is not the owner of the channel
		elif str(ctx.author.id) != row["owner_id"]:
			return await ctx.send(f"Only the creator of the room can extend the lifetime of the chanel.")

		# Update the lifetime
		await ctx.bot.pool.execute(PrivateChannelsSQL.UPDATE_LIFETIME, str(ctx.guild.id), str(ctx.channel.id), 6.0)

		await ctx.send("This channels lifetime has been extended by 6 hours.")


def setup(bot):
	bot.add_cog(PrivateChannels(bot))
