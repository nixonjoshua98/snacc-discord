import discord

from discord.ext import commands

import datetime as dt

from src import inputs


class Arguments:
	def __init__(self, *args, **kwargs):
		self.args = args
		self.kwargs = kwargs


class Server_701056373797945386(commands.Cog):
	@commands.command(name="apply", hidden=True)
	async def apply(self, ctx):
		if ctx.guild.id != 701056373797945386:
			return

		await ctx.send("I have DM'ed you")

		await ctx.author.send("If you wish to join OwO please fill in this application")

		questions = {
			"in game name": (inputs.get_input, Arguments(ctx, "What is your in-game-name?", send_dm=True)),

			"level": (
				inputs.get_input,
				Arguments(
					ctx,
					"What is your level?",
					send_dm=True,
					validation=lambda s: s.isdigit())
			),

			"preferred world": (inputs.get_input, Arguments(ctx, "What is your preferred world?", send_dm=True)),

			"hear from": (inputs.get_input, Arguments(ctx, "Where did you hear about OwO?", send_dm=True)),

			"join reason": (inputs.get_input, Arguments(ctx, "What is your reason for joining?", send_dm=True)),
		}

		answers = dict()

		# - - - ASK QUESTIONS - - - #

		for k in questions:
			func, args = questions[k]

			response = await func(*args.args, **args.kwargs)

			if response is None:
				return self.apply.reset_cooldown(ctx)

			answers[k] = response

		await ctx.author.send("Your application is complete!")

		#  - - - LOG RESULTS - - - #

		channel = ctx.bot.get_channel(737205536197443635)

		embed = discord.Embed(title="OwO Application", colour=discord.Color.orange())

		for k, v in answers.items():
			embed.add_field(name=k.title(), value=v, inline=False)

		embed.timestamp = dt.datetime.utcnow()

		embed.set_footer(text=f"{str(ctx.author)}", icon_url=ctx.author.avatar_url)

		await channel.send(embed=embed)


def setup(bot):
	bot.add_cog(Server_701056373797945386())
