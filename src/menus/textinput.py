import discord
import asyncio

from src.menus.menubase import MenuBase


class TextInputBase(MenuBase):
    def __init__(self, bot, author, question):
        super(TextInputBase, self).__init__(bot, timeout=60.0 * 5)

        self._question = question
        self._author = author

        self._response = None

    def get(self):
        return self._response

    async def send(self, destination: discord.abc.Messageable):
        self._destination = destination

        embed = discord.Embed(title=self._question, colour=discord.Color.orange())

        self._message = await destination.send(embed=embed)

        while True:
            try:
                message = await self._bot.wait_for("message", timeout=self._timeout, check=self.wait_for)

            except asyncio.TimeoutError:
                return await destination.send("Timed out.")

            else:
                self._response = message.clean_content

                break


class TextInputDM(TextInputBase):
    def wait_for(self, message: discord.Message) -> bool:
        return message.author.id == self._author.id and message.guild is None


class TextInputChannel(TextInputBase):
    def wait_for(self, message: discord.Message) -> bool:
        return message.author.id == self._author.id and message.channel.id == self._message.id
