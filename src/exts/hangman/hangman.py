import math

import discord
from discord.ext import commands

from src.common import checks
from src.common.emoji import Emoji
from src.common.queries import HangmanSQL

from .hangmanleaderboard import HangmanLeaderboard
from .hangmangame import HangmanGame, HangmanGuess


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

    @commands.command(name="words", aliases=["h"])
    async def start_hangman(self, ctx, category: str = None):
        """ Start a new words game or show the current game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            inst = HangmanGame.create_instance(category)

            if inst is not None:
                self.games[ctx.channel.id] = inst

                inst.participants.add(ctx.author.id)

                await ctx.send(f"A words game with the category `{inst.category}` has started!")

            else:
                return await self.categories(ctx)

        await inst.show_game(ctx)

    @commands.command(name="categories")
    async def categories(self, ctx):
        """ Show the available categories for words. """

        await ctx.send(f"Hangman categories include: `{', '.join(HangmanGame.get_categories())}`")

    @commands.has_permissions(administrator=True)
    @commands.command(name="giveup")
    async def giveup(self, ctx):
        """ [Admin] Give up the current words game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            return await ctx.send("No words game is currently running.")

        self.games[ctx.channel.id] = None

        await ctx.send(f"{ctx.message.author.mention} gave up on the words game.")

    @commands.command(name="skip")
    async def skip(self, ctx):
        """ Vote to skip the current words game. """

        inst: HangmanGame = self.games.get(ctx.channel.id, None)

        if inst is None:
            return await ctx.send("No words game is currently running.")

        elif ctx.author.id not in inst.participants:
            return await ctx.send("You are not currently in any words game.")

        elif ctx.author.id in inst.skip_votes:
            return await ctx.send("You have already voted to skip.")

        num_participants = len(inst.participants)
        votes_needed = 1 if num_participants == 1 else max(2, math.ceil(num_participants / 2))

        inst.skip_votes.add(ctx.author.id)

        num_votes = len(inst.skip_votes)

        if num_votes >= votes_needed:
            self.games[ctx.channel.id] = None

            await ctx.send("Skipped :thumbsup:")

            return await self.start_hangman(ctx)

        await ctx.send(f"Skip votes: {num_votes}/{votes_needed}")

    @checks.snaccman_only()
    @commands.command(name="cheat")
    async def cheat(self, ctx):
        """ [Snacc] Recieve a DM with the hidden word. """

        inst = self.games.get(ctx.channel.id)

        if inst is None:
            return await ctx.send("No words game is currently running.")

        try:
            await ctx.author.send(f"The hidden word is **{inst.hidden_word}**")

        except (discord.HTTPException, discord.Forbidden):
            await ctx.send("I failed to DM you.")

        else:
            await ctx.send("I have DM'ed you the hidden word.")

    @commands.cooldown(1, 60, commands.BucketType.guild)
    @commands.command(name="hlb")
    async def show_leaderboard(self, ctx):
        """ Shows the top words players. """

        await HangmanLeaderboard().send(ctx)
