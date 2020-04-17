import discord
import random

from discord.ext import commands

from bot.common.queries import HangmanSQL

from bot.structures.leaderboard import HangmanWins


class HangmanGame:
    _instances = {}
    _all_words = set()

    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guesses = set()
        self.hidden_word = self.get_word()

        HangmanGame._instances[ctx.guild.id] = self

    @staticmethod
    async def get_instance(id_):
        return HangmanGame._instances.get(id_, None)

    async def on_message(self, message: discord.Message):
        content = message.content.upper()

        # Single letter guess
        if len(content) == 1:
            if await self.check_letter(content):
                await self.show_game(message.channel)

        # Check win condition
        if await self.check_win():
            HangmanGame._instances.pop(message.guild.id, None)

            await self.bot.pool.execute(HangmanSQL.UPDATE_WINS, message.author.id)
            await message.channel.send(f"{message.author.mention} won! The word was `{self.hidden_word}`")

    async def show_game(self, dest):
        return await dest.send(f"``{self.encode_word()}``")

    async def check_letter(self, letter: str) -> bool:
        correct = letter in self.hidden_word.upper() and letter not in self.guesses

        if letter in self.hidden_word.upper() and letter not in self.guesses:
            self.guesses.add(letter.upper())

        return correct

    async def check_win(self):
        return all(char.upper() in self.guesses for char in self.hidden_word if not char.isspace())

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

            elif w.upper() in self.guesses:
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
            inst: HangmanGame = await HangmanGame.get_instance(message.guild.id)

            if inst is not None:
                await inst.on_message(message)

    @commands.command(name="hangman", aliases=["h"])
    async def hangman(self, ctx):
        """ Start a new guild hangman game or show the current game """

        game = await HangmanGame.get_instance(ctx.guild.id)

        if game is None:
            game = HangmanGame(ctx)

            await ctx.send("A hangman game has started!")

        await game.show_game(ctx)

    @commands.command(name="show")
    async def show(self, ctx):
        """ Show the current hangman game """

        game = await HangmanGame.get_instance(ctx.guild.id)

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
