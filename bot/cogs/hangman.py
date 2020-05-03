import discord
import asyncio

from datetime import datetime

from discord.ext import commands

from bot.common.queries import HangmanSQL
from bot.common.emoji import Emoji

from bot.structures.leaderboard import HangmanLeaderboard

WRONG_GUESS = 0
ALREADY_GUESSED = 1
CORRECT_GUESS = 2
INVALID_GUESS = 3


class HangmanGame:
    GUESS_COOLDOWN = 1

    _instances = dict()
    _all_words = set()

    def __init__(self, ctx):
        self.bot = ctx.bot

        self.letter_guesses = set()
        self.cooldowns = dict()
        self.lives_remaining = 10

        self.hidden_word = self.get_word()

        HangmanGame.set_instance(ctx.message, self)

    @staticmethod
    def get_instance(message):
        return HangmanGame._instances.get(message.channel.id, None)

    @staticmethod
    def set_instance(message, inst):
        HangmanGame._instances[message.channel.id] = inst

    @staticmethod
    def remove_instance(message):
        HangmanGame._instances.pop(message.channel.id, None)

    def on_message(self, message: discord.Message):
        if len(message.content) > 1 or self.user_on_cooldown(message):
            return

        check = self.check_letter_guess(message.content.upper())
        
        if check == ALREADY_GUESSED:
            return

        elif check == INVALID_GUESS:
            return

        elif check == CORRECT_GUESS:
            self.check_win(message)

        elif check == WRONG_GUESS:
            self.reduce_lives(message)

    async def show_game(self, dest):
        return await dest.send(f"`{self.encode_word()}` [{self.lives_remaining}]")

    def reduce_lives(self, message):
        self.lives_remaining -= 1

        if self.lives_remaining <= 0:
            HangmanGame.remove_instance(message)
            asyncio.create_task(message.channel.send(f"You have run out of lives. The word was `{self.hidden_word}`"))

    def user_on_cooldown(self, message):
        last_guess_time = self.cooldowns.get(message.author.id, None)

        if last_guess_time:
            seconds_since_guess = (datetime.now() - last_guess_time).total_seconds()

            # Cooldown has passed
            if seconds_since_guess >= self.GUESS_COOLDOWN:
                self.cooldowns[message.author.id] = datetime.now()

            # User still on cooldown
            else:
                asyncio.create_task(message.add_reaction(Emoji.ALARM_CLOCK))

                return True

        # user has no cooldown yet
        else:
            self.cooldowns[message.author.id] = datetime.now()

        return False

    def check_letter_guess(self, guess: str) -> int:
        """ Check the guess """

        if len(guess) != 1: return INVALID_GUESS

        if guess in self.letter_guesses: return ALREADY_GUESSED

        elif guess in self.hidden_word.upper():
            self.letter_guesses.add(guess)

            return CORRECT_GUESS

        self.letter_guesses.add(guess)

        return WRONG_GUESS

    def check_win(self, message):
        """ Check if the game has won, and do some stuff like send win messages """
        won = all(char.upper() in self.letter_guesses for char in self.hidden_word if not char.isspace())

        if won:
            HangmanGame.remove_instance(message)
            win_text = f"{message.author.mention} won! The word was `{self.hidden_word}`"
            asyncio.create_task(self.bot.pool.execute(HangmanSQL.INCREMENT_WINS, message.author.id))
            asyncio.create_task(message.channel.send(win_text))

        else:
            asyncio.create_task(self.show_game(message.channel))

    @staticmethod
    def get_word():
        """ Return a random word from the word list """
        if not HangmanGame._all_words:
            HangmanGame.get_all_words()

        word = HangmanGame._all_words.pop()

        return word

    @staticmethod
    def get_all_words():
        """ Load the word list into memory """

        with open("./bot/data/words.txt") as fh:
            HangmanGame._all_words = set(fh.read().splitlines())

    def encode_word(self):
        """ Encode the hidden word using other characters """

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
            inst: HangmanGame = HangmanGame.get_instance(message)

            if inst is not None:
                inst.on_message(message)

    @commands.command(name="hangman", aliases=["h"])
    async def hangman(self, ctx):
        """ Start a new guild hangman game or show the current game. """

        game = HangmanGame.get_instance(ctx.message)

        if game is None:
            game = HangmanGame(ctx)

            await ctx.send("A hangman game has started!")

        await game.show_game(ctx)

    @commands.command(name="show")
    async def show(self, ctx):
        """ Show the current hangman game. """

        game = HangmanGame.get_instance(ctx.message)

        if game is None:
            await ctx.send("Start a hangman game first!")

        else:
            await game.show_game(ctx)

    @commands.has_permissions(administrator=True)
    @commands.command(name="giveup")
    async def giveup(self, ctx):
        """ Give up the current hangman game. """

        game = HangmanGame.get_instance(ctx.message)

        if game is None:
            await ctx.send("Start a hangman game first!")

        else:
            HangmanGame.remove_instance(ctx.message)

            await ctx.send(f"{ctx.message.author.mention} gave on on the hangman game.")

    @commands.command(name="hlb")
    async def leaderboard(self, ctx):
        """ Shows the top hangman players. """

        return await ctx.send(await HangmanLeaderboard(ctx).create())


def setup(bot):
    bot.add_cog(Hangman(bot))
