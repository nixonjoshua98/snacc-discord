import discord

from discord.ext import commands

from bot.common.emoji import Emoji
from bot.common.queries import HangmanSQL
from bot.utils.hangman import HangmanGame, HangmanGuess
from bot.structures.leaderboard import HangmanLeaderboard


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.games = {}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.author.bot and self.bot.is_ready():
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
    async def hangman(self, ctx):
        """ Start a new guild hangman game or show the current game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            inst = HangmanGame()

            self.games[ctx.channel.id] = inst

            await ctx.send("A hangman game has started!")

        await inst.show_game(ctx)

    @commands.command(name="show")
    async def show(self, ctx):
        """ Show the current hangman game. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            await ctx.send("Start a hangman game first!")

        else:
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

            await ctx.send(f"{ctx.message.author.mention} gave on on the hangman game.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="cheat")
    async def cheat(self, ctx):
        """ [Admin] Recieve a DM with the hidden word. """

        inst = self.games.get(ctx.channel.id, None)

        if inst is None:
            await ctx.send("No hangman game running.")

        else:
            await ctx.author.send(f"'{ctx.guild.name}' (#{ctx.channel.name}): **{inst.hidden_word}**")

            await ctx.send("I have DM'ed you the hidden word.")

    @commands.command(name="hlb")
    async def leaderboard(self, ctx):
        """ Shows the top hangman players. """

        return await ctx.send(await HangmanLeaderboard(ctx).create())


def setup(bot):
    bot.add_cog(Hangman(bot))
