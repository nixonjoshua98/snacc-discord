import discord

from discord.ext import commands

import datetime as dt

from src.common import checks

from src.structs.confirm import Confirm
from src.structs.question import Question


class Questionnaire(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener("on_message")
	async def on_message(self, message):
		async def get_prefix():
			for pre in await self.bot.get_prefix(message):
				if message.content.lower().startswith(pre):
					return pre

			return None

		if message.guild is None or message.author.bot:
			return None

		elif (prefix := await get_prefix()) is None:
			return None

		args = message.content[len(prefix):].split(" ")

		if len(args) > 0:
			query = {"server": message.guild.id, "command": args[0]}

			questionnaire = await self.bot.mongo.find_one("questionnaires", query)

			if questionnaire:
				await self.send_questionnaire(message.channel, message.author, questionnaire)

	@commands.group(name="questionnaire", aliases=["qu"], hidden=True)
	async def group(self, ctx):
		""" Group command. """

	@commands.check_any(commands.has_permissions(administrator=True), checks.snaccman_only())
	@group.command(name="create")
	async def create_questionnaire(self, ctx):
		""" Create a questionnaire for your server. """

		title = await self.get_title(ctx)
		questions = await self.get_questions(ctx)
		log_channel = await self.get_log_channel(ctx)
		comm = await self.get_comm(ctx)

		row = dict(title=title, server=ctx.guild.id, command=comm, log_channel=log_channel.id, questions=questions)

		await ctx.bot.mongo.insert_one("questionnaires", row)

		await ctx.send("Questionnaire created!")

	@commands.check_any(commands.has_permissions(administrator=True), checks.snaccman_only())
	@group.command(name="delete")
	async def delete_questionnaire(self, ctx, comm: str):
		""" Delete a questionnaire from your server. """

		comm = comm.lower()

		query = {"server": ctx.guild.id, "command": comm}

		existing = await ctx.bot.mongo.find_one("questionnaires", query)

		if existing:
			await ctx.bot.mongo.delete_one("questionnaires", query)

			await ctx.send(f"Questionnaire **{comm}** has been deleted.")

		else:
			await ctx.send(f"I could not find the questionnaire **{comm}**")

	async def send_questionnaire(self, from_channel, author, questionnaire):
		await from_channel.send("I have DM'ed you")

		embed = discord.Embed(title=questionnaire["title"], colour=discord.Color.orange())

		# - - - ASK QUESTIONS - - - #

		for question in questionnaire["questions"]:

			response = await Question(self.bot, author, question).prompt(author)

			if response is None:
				return None

			embed.add_field(name=question, value=response, inline=False)

		await author.send("Your application is complete!")

		#  - - - LOG RESULTS - - - #

		server = self.bot.get_guild(questionnaire["server"])

		log_channel = server.get_channel(questionnaire["log_channel"])

		if log_channel is None:
			log_channel = from_channel

			await log_channel.send("I could not find the designated log channel.")

		embed.timestamp = dt.datetime.utcnow()

		embed.set_footer(text=f"{str(author)}", icon_url=author.avatar_url)

		await log_channel.send(embed=embed)

	@staticmethod
	async def get_questions(ctx):
		questions = []

		# - Get questions for questionnaire
		while True:
			txt = f"**Question {len(questions) + 1}**: What is your question?"

			question = await Question(ctx.bot, ctx.author, txt).prompt(ctx)

			if question is None:
				raise commands.CommandError("Questionnaire creation has been aborted.")

			questions.append(question)

			another_question = await Confirm("Add another question?", timeout=300.0).prompt(ctx)

			if another_question is None or not another_question:
				break

		return questions

	@staticmethod
	async def get_log_channel(ctx):
		while True:
			channel_name = await Question(ctx.bot, ctx.author, f"Where should I log the answers?").prompt(ctx)

			if channel_name is None:
				raise commands.CommandError("Questionnaire creation has been aborted.")

			channel = discord.utils.get(ctx.guild.channels, name=channel_name)

			if channel is None:
				await ctx.send(f"I could not a find channel with the name **{channel_name}**")

			elif not ctx.bot.has_permission(channel, send_messages=True):
				await ctx.send(f"I do not have write permissions in {channel.mention}")

			else:
				return channel

	@staticmethod
	async def get_comm(ctx):
		while True:
			txt = f"Which command should the questionnaire be attached to? eg {ctx.prefix}apply"

			comm = await Question(ctx.bot, ctx.author, txt).prompt(ctx)

			if comm is None:
				raise commands.CommandError("Questionnaire creation has been aborted.")

			elif comm.split(" ") > 0:
				ctx.send("Commands must be a single word.")
				continue

			existing = await ctx.bot.mongo.find_one("questionnaires", {"server": ctx.guild.id, "command": comm})

			if existing:
				await ctx.send(f"You already have a questionnaire attached to **{ctx.prefix}{comm}**")

			else:
				return comm.lower()

	@staticmethod
	async def get_title(ctx):
		while True:
			txt = "What title should the questionnaire have when I log the results?"

			title = await Question(ctx.bot, ctx.author, txt).prompt(ctx)

			if title is None:
				raise commands.CommandError("Questionnaire creation has been aborted.")

			else:
				return title


def setup(bot):
	bot.add_cog(Questionnaire(bot))
