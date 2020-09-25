import asyncio
import discord

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
	@commands.command(name="purge", usage="<user=None> <limit=0>", cooldown_after_parsing=True)
	async def purge(self, ctx, user: Optional[discord.Member] = None, limit: Range(0, 100) = 0):
		""" Clear a channel of messages. """

		async def target_user():
			messages_deleted = 0

			async for msg in ctx.channel.history(limit=500):
				if messages_deleted >= limit:
					break

				elif msg.author.id == user.id:
					await msg.delete()

					messages_deleted += 1

			return messages_deleted

		if user is None:
			if (deleted := len(await ctx.channel.purge(limit=limit))) > 0:
				self.log_action(ctx, title=f"Channel Purge [{deleted} message(s)]", channel=ctx.channel.mention)

		else:
			if (deleted := await target_user()) > 0:
				chnl = ctx.channel.mention

				self.log_action(ctx, title=f"Channel Purge [{deleted} message(s)]", channel=chnl, user=user.mention)

		await ctx.send(f"Deleted {deleted:,} message(s)")


def setup(bot):
	bot.add_cog(Moderator())
