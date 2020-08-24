import discord
import asyncio

from discord.ext import commands


class Question:
	def __init__(self, bot, author, question, **kwargs):
		self.bot = bot

		self.author = author
		self.question = question

		self.message = None
		self.destination = None

		self.timeout = kwargs.get("timeout", 300.0)

	def wait_for(self, message):
		if isinstance(self.destination, (discord.Member, discord.User)):
			return message.author.id == self.author.id

		elif isinstance(self.destination, discord.TextChannel):
			return message.author.id == self.author.id and message.channel.id == self.destination.id

		elif isinstance(self.destination, commands.Context):
			return message.author.id == self.author.id and message.channel.id == self.destination.channel.id

	async def send_initial_message(self, destination) -> discord.Message:
		embed = self.bot.embed(title=self.question)

		return await destination.send(embed=embed)

	async def on_exit(self):
		embed = self.bot.embed(title=self.question)

		embed.add_field(name="Response", value="Timed Out")

		await self.message.edit(embed=embed)

	async def on_response(self, resp):
		embed = self.bot.embed(title=self.question)

		embed.add_field(name="Response", value=resp)

		await self.message.edit(embed=embed)

	async def prompt(self, destination):
		self.destination = destination

		self.message = await self.send_initial_message(destination)

		while True:
			try:
				message = await self.bot.wait_for("message", timeout=self.timeout, check=self.wait_for)

			except asyncio.TimeoutError:
				await self.on_exit()

				return None

			else:
				await self.on_response(message.clean_content)

				return message.clean_content
