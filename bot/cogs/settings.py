import discord

from discord.ext import commands

from bot.common import checks
from bot.common.converters import RoleTag
from bot.common.queries import ServersSQL


class Settings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_check(self, ctx: commands.Context):
		return checks.author_is_server_owner(ctx) or await self.bot.is_owner(ctx.author)

	async def cog_before_invoke(self, ctx: commands.Context):
		_ = await self.bot.get_server(ctx.guild)

	async def cog_after_invoke(self, ctx):
		await self.bot.update_server_cache(ctx.message.guild)

	@commands.command(name="prefix")
	async def set_prefix(self, ctx: commands.Context, prefix: str):
		""" Set the prefix for this server. """

		await ctx.bot.pool.execute(ServersSQL.UPDATE_PREFIX, ctx.guild.id, prefix)

		await ctx.send(f"Server prefix has been updated to **{prefix}**")

	@commands.command(name="setrole")
	async def set_role(self, ctx, tag: RoleTag(), role: discord.Role = 0):
		""" Tag a selected role, which can open up new commands. """

		table = {"entry": ServersSQL.UPDATE_ENTRY_ROLE, "member": ServersSQL.UPDATE_MEMBER_ROLE}

		q = table[tag]

		if role == 0:
			await ctx.bot.pool.execute(q, ctx.guild.id, role)

			await ctx.send(f"Tagged role `{tag}` has been removed")

		else:
			if tag == "entry" and role > ctx.guild.me.top_role:
				return await ctx.send(f"I cannot use the role **{role.name}**. The role is higher than me")

			await ctx.bot.pool.execute(q, ctx.guild.id, role.id)

			await ctx.send(f"Tagged role `{tag}` has been set to `{role.name}`")


def setup(bot):
	bot.add_cog(Settings(bot))
