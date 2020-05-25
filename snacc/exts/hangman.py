import os
import enum
import time
import json
import random

import discord
from discord.ext import commands

from typing import Union

from snacc.common.emoji import UEmoji
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
    __word_cache = None

    def __init__(self, category: str = None):
        self.category = category

        self.cooldowns = dict()
        self.letter_guesses = set()

        self.lives_remaining = 10

        self.hidden_word = self.get_new_word(category)

    @staticmethod
    def create_instance(category: Union[None, str]):
        HangmanGame.load_words()

        if category is None:
            category = random.choice(HangmanGame.get_categories())

            return HangmanGame(category)

        elif category.lower() in HangmanGame.__word_cache.keys():
            return HangmanGame(category.lower())

        return None

    def on_message(self, message: discord.Message):
        guess = message.content.upper().strip()

        if not self.is_valid_guess(guess):
            return None

        elif self.is_user_on_cooldown(message.author):
            return HangmanGuess.USER_ON_COOLDOWN

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
        return len(guess) == 1 and guess in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def is_user_on_cooldown(self, author: discord.Member) -> bool:
        now = time.time()

        cooldown = self.cooldowns.get(author.id, None)

        if cooldown is None or (now - cooldown >= 1.5):
            self.cooldowns[author.id] = now
            return False

        return True

    def check_win(self):
        return all(char.upper() in self.letter_guesses for char in self.hidden_word if not char.isspace())

    def encode_word(self) -> str:
        ls = []

        for char in self.hidden_word:
            upper = char.upper()

            if char.isspace():
                ls.append("/")

            elif upper in self.letter_guesses:
                ls.append(char)

            else:
                ls.append("_")

        return " ".join(ls)

    @staticmethod
    def load_words():
        if HangmanGame.__word_cache is None:
            with open(os.path.join(os.getcwd(), "snacc", "data", "words.json")) as fh:
                HangmanGame.__word_cache = json.load(fh)

    @staticmethod
    def get_new_word(category: str) -> str:
        return random.choice(HangmanGame.__word_cache[category])

    @staticmethod
    def get_categories() -> tuple:
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
                    await message.add_reaction(UEmoji.ALARM_CLOCK)

                elif result == HangmanGuess.GAME_WON:
                    self.games[message.channel.id] = None

                    await self.bot.pool.execute(HangmanSQL.ADD_WIN, message.author.id)

                    await message.channel.send(f"{message.author.mention} won! The word was `{inst.hidden_word}`")

                elif result == HangmanGuess.GAME_OVER:
                    self.games[message.channel.id] = None

                    await message.channel.send(f"You have run out of lives. The word was `{inst.hidden_word}`")

    @commands.command(name="hangman", aliases=["h"])
    async def hangman(self, ctx, category: str = None):
        """ Start a new hangman game or show the current game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            inst = HangmanGame.create_instance(category)

            if inst is not None:
                self.games[ctx.channel.id] = inst

                await ctx.send(f"A hangman game with category `{inst.category}` has started!")

            else:
                return await ctx.send(f"Categories include: `{', '.join(HangmanGame.get_categories())}`")

        await inst.show_game(ctx)

    @commands.has_permissions(administrator=True)
    @commands.command(name="giveup")
    async def giveup(self, ctx):
        """ [Admin] Give up the current hangman game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            await ctx.send("Start a hangman game first!")

        else:
            self.games[ctx.channel.id] = None

            await ctx.send(f"{ctx.message.author.mention} gave up on the hangman game.")

    @commands.is_owner()
    @commands.command(name="cheat")
    async def cheat(self, ctx):
        """ [Creator] Recieve a DM with the hidden word. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            await ctx.send("No hangman game running.")

        else:
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
