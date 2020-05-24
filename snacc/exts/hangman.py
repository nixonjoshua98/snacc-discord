import discord
import string
import enum
import time

from discord.ext import commands

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
    _word_cache = set()

    def __init__(self):
        self.letter_guesses = set()
        self.cooldowns = dict()

        self.lives_remaining = 10

        self.hidden_word = self.get_new_word()

    def on_message(self, message: discord.Message):
        guess = message.content.upper()

        if not self.is_valid_guess(guess):
            return None

        elif self.is_user_on_cooldown(message.author):
            return HangmanGuess.USER_ON_COOLDOWN

        return self.check_guess(guess)

    async def show_game(self, dest):
        return await dest.send(f"`{self.encode_word()}` [{self.lives_remaining}]")

    def is_game_over(self):
        return self.lives_remaining <= 0

    def is_valid_guess(self, guess):
        return len(guess) == 1 and guess in string.ascii_uppercase

    def is_user_on_cooldown(self, author: discord.Member) -> bool:
        now = time.time()

        cooldown = self.cooldowns.get(author.id, None)

        if cooldown is None or (now - cooldown >= 1.5):
            self.cooldowns[author.id] = now
            return False

        return True

    def check_guess(self, guess: str) -> HangmanGuess:
        if guess in self.letter_guesses:
            return HangmanGuess.ALREADY_GUESSED

        elif guess in self.hidden_word.upper():
            self.letter_guesses.add(guess)

            return HangmanGuess.GAME_WON if self.check_win() else HangmanGuess.CORRECT_GUESS

        self.letter_guesses.add(guess)

        self.lives_remaining -= 1

        return HangmanGuess.GAME_OVER if self.is_game_over() else HangmanGuess.WRONG_GUESS

    def check_win(self):
        return all(char.upper() in self.letter_guesses for char in self.hidden_word if not char.isspace())

    def encode_word(self) -> str:
        return " ".join([w if w.upper() in self.letter_guesses else "_" for w in self.hidden_word])

    @staticmethod
    def get_new_word() -> str:
        if not HangmanGame._word_cache:
            with open("./snacc/data/words.txt") as fh:
                HangmanGame._word_cache = set(fh.read().splitlines())

        return HangmanGame._word_cache.pop()


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
    async def hangman(self, ctx):
        """ Start a new hangman game or show the current game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            inst = HangmanGame()

            self.games[ctx.channel.id] = inst

            await ctx.send("A hangman game has started!")

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
