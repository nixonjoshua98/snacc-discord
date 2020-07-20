import discord
import asyncio

from .inputbase import InputBase


class TextInputBase(InputBase):
    def __init__(self, bot, author, question, *, validation=None):
        super().__init__(bot, author, timeout=300.0)

        self._question = question
        self._validation_func = validation

        self._response = None

    def get(self):
        return self._response

    async def send_initial_message(self, destination) -> discord.Message:
        embed = discord.Embed(title=self._question, colour=discord.Color.orange())

        return await destination.send(embed=embed)

    async def on_exit(self):
        embed = self.message.embeds[0]

        embed.description = "Timed out"

        await self.edit_message(embed=embed)

    async def send(self, destination):
        await super(TextInputBase, self).send(destination)

        while True:
            try:
                message = await self.bot.wait_for("message", timeout=self.timeout, check=self.wait_for)

            except asyncio.TimeoutError:
                return await self.on_exit()

            else:
                response = message.clean_content

                embed = self.message.embeds[0]

                if self._validation_func is None or self._validation_func(response):
                    embed.description = self._response = response

                    await self.edit_message(embed=embed)

                    break

                else:
                    embed.description = f"`{response[0:50]}` is not a valid answer."

                    await self.edit_message(embed=embed)


class TextInputDM(TextInputBase):
    def wait_for(self, message: discord.Message) -> bool:
        return message.author.id == self.author.id and message.guild is None


class TextInputChannel(TextInputBase):
    def wait_for(self, message: discord.Message) -> bool:
        return message.author.id == self.author.id and message.channel.id == self.destination.id
