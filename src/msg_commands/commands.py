import discord
import random


async def on_message_commands(message):
	val = random.randint(0, 100)

	if val <= 5:
		await mock_message(message)


async def mock_message(message: discord.Message):
	def mock(text):
		msg = []

		for i, char in enumerate(text):
			if char == " ":
				msg.append(" ")
				continue

			msg.append(f"*{char.lower()}*" if i % 2 == 1 else f"*{char.upper()}*")

		return " ".join(msg)

	if len(message.clean_content) <= 25:
		await message.channel.send(mock(message.clean_content))