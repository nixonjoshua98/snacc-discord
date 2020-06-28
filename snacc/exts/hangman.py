import os
import enum
import math
import time
import string
import random

import discord
from discord.ext import commands

from typing import Union

from snacc.common.emoji import Emoji
from snacc.common.queries import HangmanSQL

from snacc.structs.leaderboards import HangmanLeaderboard


class HangmanGuess(enum.IntEnum):
    GAME_WON = 0
    GAME_OVER = 1
    WRONG_GUESS = 2
    CORRECT_GUESS = 3
    ALREADY_GUESSED = 4
    USER_ON_COOLDOWN = 5


class HangmanGame:
    __word_cache = dict()

    def __init__(self, category: str = None):
        self.category = category

        self.cooldowns = dict()
        self.skip_votes = set()
        self.participants = set()
        self.letter_guesses = set()

        self.lives_remaining = 10

        self.hidden_word = self.get_new_word(category)

    @staticmethod
    def create_instance(category: Union[str, None]):
        HangmanGame.load_words()

        if category is None:
            category = random.choice(HangmanGame.get_categories())

        if category.lower() in HangmanGame.__word_cache.keys():
            return HangmanGame(category.lower())

        return None

    def on_message(self, message: discord.Message):
        guess = message.content.upper().strip()

        if not self.is_valid_guess(guess):
            return None

        elif self.is_user_on_cooldown(message.author):
            return HangmanGuess.USER_ON_COOLDOWN

        self.participants.add(message.author)

        return self.check_guess(guess)

    def check_guess(self, guess: str) -> HangmanGuess:
        if guess in self.letter_guesses:
            return HangmanGuess.ALREADY_GUESSED

        elif guess in self.hidden_word.upper():
            self.letter_guesses.add(guess)

            if self.check_win():
                return HangmanGuess.GAME_WON

            return HangmanGuess.CORRECT_GUESS

        self.letter_guesses.add(guess)

        self.lives_remaining -= 1

        return HangmanGuess.GAME_OVER if self.is_game_over() else HangmanGuess.WRONG_GUESS

    async def show_game(self, dest):
        return await dest.send(f"`{self.encode_word()} [{self.lives_remaining}]`")

    def is_game_over(self):
        return self.lives_remaining <= 0

    def is_valid_guess(self, guess):
        return len(guess) == 1 and guess in string.ascii_uppercase + string.digits

    def is_user_on_cooldown(self, author: discord.Member) -> bool:
        now = time.time()

        cooldown = self.cooldowns.get(author.id, None)

        if cooldown is None or (now - cooldown >= 1.5):
            self.cooldowns[author.id] = now
            return False

        return True

    def check_win(self) -> bool:
        alphanum = string.ascii_uppercase + string.digits

        return all(char.upper() in self.letter_guesses for char in self.hidden_word if char.upper() in alphanum)

    def encode_word(self) -> str:
        ls = []

        for char in self.hidden_word:
            upper = char.upper()

            if char.isspace():
                ls.append("/")

            elif upper in self.letter_guesses or char in string.punctuation:
                ls.append(char)

            else:
                ls.append("_")

        return " ".join(ls)

    @staticmethod
    def load_words():
        if not HangmanGame.__word_cache:
            for root, dirs, files in os.walk(os.path.join(os.getcwd(), "snacc", "data", "hangman")):
                for f in files:
                    if f.endswith(".txt"):
                        category = f.replace(".txt", "")
                        path = os.path.join(root, f)

                        with open(path, "r") as fh:
                            HangmanGame.__word_cache[category] = fh.read().splitlines()

    @staticmethod
    def get_new_word(category: str) -> str:
        return random.choice(HangmanGame.__word_cache[category])

    @staticmethod
    def get_categories() -> tuple:
        HangmanGame.load_words()

        return tuple(HangmanGame.__word_cache.keys())


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.games = {}

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        if await self.bot.on_message_check(message):
            inst = self.games.get(message.channel.id, None)

            if inst is not None:
                result = inst.on_message(message)

                if result == HangmanGuess.CORRECT_GUESS:
                    await inst.show_game(message.channel)

                elif result == HangmanGuess.USER_ON_COOLDOWN:
                    await message.add_reaction(Emoji.ALARM_CLOCK)

                elif result == HangmanGuess.GAME_WON:
                    self.games[message.channel.id] = None

                    await self.bot.pool.execute(HangmanSQL.ADD_WIN, message.author.id)

                    await message.channel.send(f"{message.author.mention} won! The word was `{inst.hidden_word}`")

                elif result == HangmanGuess.GAME_OVER:
                    self.games[message.channel.id] = None

                    await message.channel.send(f"You have run out of lives. The word was `{inst.hidden_word}`")

    @commands.command(name="hangman", aliases=["h"])
    async def start_hangman(self, ctx, category: str = None):
        """ Start a new hangman game or show the current game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            inst = HangmanGame.create_instance(category)

            if inst is not None:
                self.games[ctx.channel.id] = inst

                inst.participants.add(ctx.author.id)

                await ctx.send(f"A hangman game with the category `{inst.category}` has started!")

            else:
                return await self.categories(ctx)

        await inst.show_game(ctx)

    @commands.command(name="categories")
    async def categories(self, ctx):
        """ Show the available categories for hangman. """

        await ctx.send(f"Hangman categories include: `{', '.join(HangmanGame.get_categories())}`")

    @commands.has_permissions(administrator=True)
    @commands.command(name="giveup")
    async def giveup(self, ctx):
        """ [Admin] Give up the current hangman game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            return await ctx.send("No hangman game is currently running.")

        self.games[ctx.channel.id] = None

        await ctx.send(f"{ctx.message.author.mention} gave up on the hangman game.")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """ Vote to skip the current hangman game. """

        inst: HangmanGame = self.games.get(ctx.channel.id, None)

        if inst is None:
            return await ctx.send("No hangman game is currently running.")

        elif ctx.author not in inst.participants:
            return await ctx.send("You are not currently in any hangman game.")

        elif ctx.author.id in inst.skip_votes:
            return await ctx.send("You have already voted to skip.")

        num_participants = len(inst.participants)
        votes_needed = max(2, math.ceil(num_participants / 2))

        inst.skip_votes.add(ctx.author.id)

        num_votes = len(inst.skip_votes)

        if num_votes >= votes_needed:
            self.games[ctx.channel.id] = None

            await ctx.send("Skipped :thumbsup:")

            return await self.start_hangman(ctx)

        await ctx.send(f"Skip votes: {num_votes}/{votes_needed}")

    @commands.is_owner()
    @commands.command(name="cheat")
    async def cheat(self, ctx):
        """ [Creator] Recieve a DM with the hidden word. """

        inst = self.games.get(ctx.channel.id)

        if inst is None:
            return await ctx.send("No hangman game is currently running.")

        try:
            await ctx.author.send(f"The hidden word is **{inst.hidden_word}**")

        except (discord.HTTPException, discord.Forbidden):
            await ctx.send("I failed to DM you.")

        else:
            await ctx.send("I have DM'ed you the hidden word.")

    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.command(name="hlb")
    async def show_leaderboard(self, ctx):
        """ Shows the top hangman players. """

        await HangmanLeaderboard().send(ctx)


def setup(bot):
    bot.add_cog(Hangman(bot))
