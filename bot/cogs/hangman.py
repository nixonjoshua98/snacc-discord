import discord
import asyncio

from discord.ext import commands

from bot.common.queries import HangmanSQL

from bot.structures.leaderboard import HangmanWins


class HangmanGame:
    _instances = dict()
    _all_words = set()

    def __init__(self, ctx):
        self.bot = ctx.bot

        self.word_guesses = set()
        self.letter_guesses = set()

        self.hidden_word = self.get_word()

        HangmanGame._instances[ctx.guild.id] = self

    @staticmethod
    def get_instance(id_):
        return HangmanGame._instances.get(id_, None)

    def on_message(self, message: discord.Message):
        content = message.content.upper()

        if self.check_letter(content) or self.check_word(content):
            if self.check_win():
                HangmanGame._instances.pop(message.guild.id, None)

                win_text = f"{message.author.mention} won! The word was `{self.hidden_word}`"

                asyncio.create_task(self.bot.pool.execute(HangmanSQL.UPDATE_WINS, message.author.id))
                asyncio.create_task(message.channel.send(win_text))

            else:
                asyncio.create_task(self.show_game(message.channel))

    async def show_game(self, dest):
        return await dest.send(f"``{self.encode_word()}``")

    def check_letter(self, guess: str) -> bool:
        if len(guess) != 1:
            return False

        correct = guess in self.hidden_word.upper() and guess not in self.letter_guesses

        self.letter_guesses.add(guess)

        return correct

    def check_word(self, guess: str) -> bool:
        if len(guess) <= 1:
            return False

        self.word_guesses.add(guess)

        return guess == self.hidden_word.upper()

    def check_win(self):
        correct_words = self.hidden_word.upper() in self.word_guesses
        correct_letters = all(char.upper() in self.letter_guesses for char in self.hidden_word if not char.isspace())

        return correct_words or correct_letters

    @staticmethod
    def get_word():
        if not HangmanGame._all_words:
            HangmanGame.get_all_words()

        word = HangmanGame._all_words.pop()

        return word

    @staticmethod
    def get_all_words():
        with open("./bot/data/words.txt") as fh:
            HangmanGame._all_words = set(fh.read().splitlines())

    def encode_word(self):
        s = []

        for w in self.hidden_word:
            if w.isspace():
                s.append("/")

            elif w.upper() in self.letter_guesses:
                s.append(w)

            else:
                s.append("_")

        return " ".join(s)


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.games = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot:
            inst: HangmanGame = HangmanGame.get_instance(message.guild.id)

            if inst is not None:
                inst.on_message(message)

    @commands.command(name="hangman", aliases=["h"])
    async def hangman(self, ctx):
        """
Start a new guild hangman game or show the current game

__How to Play__
Guess a letter or word by giving a guess without any prefix.
"""
        game = HangmanGame.get_instance(ctx.guild.id)

        if game is None:
            game = HangmanGame(ctx)

            await ctx.send("A hangman game has started!")

        await game.show_game(ctx)

    @commands.command(name="show")
    async def show(self, ctx):
        """ Show the current hangman game """

        game = HangmanGame.get_instance(ctx.guild.id)

        if game is None:
            await ctx.send("Start a hangman game first!")

        else:
            await game.show_game(ctx)

    @commands.command(name="hlb")
    async def leaderboard(self, ctx):
        """ Shows the top hangman players """

        return await ctx.send(await HangmanWins(ctx).create())


def setup(bot):
    bot.add_cog(Hangman(bot))
