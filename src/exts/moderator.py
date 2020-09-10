import asyncio
import discord

from discord.ext import commands

from src.common import checks
from src.common.converters import Range

from typing import Optional


class Moderator(commands.Cog):
	__override_channel_whitelist__ = True

	async def log_action(self, ctx, *, title, **kwargs):
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
	@commands.cooldown(1, 15, commands.BucketType.member)
	@commands.command(name="purge", usage="<user=None> <limit=0>", cooldown_after_parsing=True)
	async def purge(self, ctx, user: Optional[discord.Member] = None, limit: Range(0, 100) = 0):
		""" Clear a channel of messages. """

		def check(m):
			return user is None or m.author.id == user.id

		try:
			deleted = await ctx.channel.purge(limit=limit, check=check)

		except (discord.HTTPException, discord.Forbidden):
			return await ctx.send("Channel purge failed.")

		if len(deleted) > 0:
			await self.log_action(ctx, title=f"Channel Purge [{len(deleted)} message(s)]", channel=ctx.channel.mention)

		await ctx.send(f"Deleted {len(deleted):,} message(s)")


def setup(bot):
	bot.add_cog(Moderator())
