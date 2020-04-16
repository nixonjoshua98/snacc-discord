import discord
import random
import asyncio

from discord.ext import commands


class HangmanGame:
    _instances = {}
    _all_words = []

    def __init__(self, ctx):
        HangmanGame._instances[ctx.guild.id] = self

        self.ctx = ctx
        self.guesses = []
        self.hidden_word = self.get_word()

        asyncio.create_task(self.run())

    @staticmethod
    async def get_instance(id_):
        return HangmanGame._instances.get(id_, None)

    @staticmethod
    def get_word():
        if not HangmanGame._all_words:
            HangmanGame.get_all_words()

        index = random.randint(0, len(HangmanGame._all_words) - 1)

        return HangmanGame._all_words.pop(index)

    @staticmethod
    def get_all_words():
        with open("./bot/data/words.txt") as fh:
            HangmanGame._all_words = fh.read().splitlines()

    async def run(self):
        await self.ctx.send("Hangman game has started!")

        destination = self.ctx.channel

        while True:
            encoded = self.encode_word()

            await destination.send("``" + encoded + "``")

            try:
                message = await self.ctx.bot.wait_for("message", timeout=60 * 60, check=self.wait_for_guess)

            except asyncio.TimeoutError:
                HangmanGame._instances.pop(self.ctx.guild.id, None)
                break

            else:
                self.guesses.append(message.content.upper())

                destination = message.channel

                if self.is_game_over():
                    HangmanGame._instances.pop(self.ctx.guild.id, None)

                    return await destination.send(
                        f"{message.author.mention} got the final letter! The word was `{self.hidden_word}`")

                await destination.send(f"`{message.content.upper()}` was a correct guess!")

    def wait_for_guess(self, message: discord.Message):
        return message.guild.id == self.ctx.guild.id and not message.author.bot and self.correct_guess(message.content)

    def encode_word(self):
        s = []

        for w in self.hidden_word:
            if w.isspace():
                s.append("/")

            elif w.upper() in self.guesses:
                s.append(w)

            else:
                s.append("_")

        return " ".join(s)

    def is_game_over(self):
        return all(char.upper() in self.guesses for char in self.hidden_word if not char.isspace())

    def correct_guess(self, guess: str):
        return len(guess) == 1 and guess.upper() in self.hidden_word.upper() and guess.upper() not in self.guesses


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.games = {}

    @commands.command(name="hangman", aliases=["hang", "h"])
    async def hangman(self, ctx):
        """ Start a new guild hangman game """
        game = await HangmanGame.get_instance(ctx.guild.id)

        if game is None:
            self.games[ctx.guild.id] = HangmanGame(ctx)
        else:
            return await ctx.send("A hangman game is already in progress")

    @commands.command(name="show")
    async def show(self, ctx):
        """ Show the current hangman game """

        game = await HangmanGame.get_instance(ctx.guild.id)

        if game is None:
            return await ctx.send("Start a hangman game first!")
        else:
            return await ctx.send(f"``{game.encode_word()}``")


def setup(bot):
    bot.add_cog(Hangman(bot))
