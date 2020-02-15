import discord
import random


async def on_message_commands(message):
	val = random.randint(0, 100)

	if not message.mentions:
		if val <= 10 and len(message.clean_content) <= 50:
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

	await message.channel.send(mock(message.clean_content))
