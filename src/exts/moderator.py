import asyncio
import discord

import datetime as dt

from discord.ext import commands

from src.common import checks
from src.common.converters import Range

from typing import Optional


class Moderator(commands.Cog):
	__override_channel_whitelist__ = True

	def log_action(self, ctx, *, title, **kwargs):
		async def log_action_task():
			svr = await ctx.bot.db["servers"].find_one({"_id": ctx.guild.id}) or dict()

			if (log_chnl := svr.get("log_channel")) is not None:
				log_chnl = ctx.guild.get_channel(log_chnl)

				if log_chnl is not None and ctx.bot.has_permissions(log_chnl, send_messages=True):
					embed = ctx.bot.embed(title=title)

					embed.add_field(name="Moderator", value=ctx.author.mention)

					for k, v in kwargs.items():
						embed.add_field(name=k.title(), value=v)

					await log_chnl.send(embed=embed)

		asyncio.create_task(log_action_task())

	@checks.is_admin()
	@commands.command(name="logchannel")
	async def set_log_channel(self, ctx, *, channel: discord.TextChannel = None):
		""" Set the log channel for Moderator actions. """

		if channel is None:
			query = {"$unset": {"log_channel": None}}

			await ctx.send("I have unset the log channel.")

		else:
			query = {"$set": {"log_channel": channel.id}}

			await ctx.send(f"I will log moderator actions to {channel.mention}")

		await ctx.bot.db["servers"].update_one({"_id": ctx.guild.id}, query, upsert=True)

	@checks.is_mod()
	@commands.max_concurrency(1, commands.BucketType.channel)
	@commands.bot_has_permissions(manage_messages=True)
	@commands.command(name="purge", usage="<user> <num>")
	async def purge_command(self, ctx, user: Optional[discord.Member] = None, amount: Range(1, 100) = 0):
		""" Purge messages from channel. Checks up to **7** days in the past or **250** messages. """

		seven_days_ago = dt.datetime.utcnow() - dt.timedelta(days=7)

		async def purge():
			messages = []

			async for msg in ctx.channel.history(limit=250, after=seven_days_ago, oldest_first=False):
				if len(messages) >= amount:
					break

				elif msg.id == ctx.message.id:
					continue

				elif user is None or msg.author.id == user.id:
					messages.append(msg)

			# We can only bulk delete a max of 100 messages
			await ctx.channel.delete_messages(messages)

			return len(messages)

		deleted = await purge()

		if user is None and deleted > 0:
			self.log_action(ctx, title=f"Channel Purge [{deleted} message(s)]", channel=ctx.channel.mention)

		elif user is not None and deleted > 0:
			chnl = ctx.channel.mention

			self.log_action(ctx, title=f"Channel Purge [{deleted} message(s)]", channel=chnl, user=user.mention)

		await ctx.send(f"Deleted {deleted:,} message(s)")



def setup(bot):
	bot.add_cog(Moderator())
