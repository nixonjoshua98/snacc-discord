import time
import discord
import random
import asyncio

from discord.ext import commands

from bot.structures import TimerLeaderboard

from bot.common import (
    checks,
)

from bot.common import (
    ChannelTags,
    DBConnection,
    MinigamesSQL
)


class Minigames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.games = dict()
        self.leaderboards = dict()

    def cog_check(self, ctx):
        return checks.channel_has_tag(ctx, ChannelTags.GAME)

    @commands.command(name="t", help="Time game")
    async def timer_game(self, ctx: commands.Context):
        def check(m: discord.Message):
            return m.channel.id == ctx.channel.id and m.content.lower() == "now" and not m.author.bot

        # Ignore the call if a game is ongoing
        if self.games.get(ctx.channel.id, {}).get("ongoing", False):
            return

        game_duration = random.randint(3, 10)

        self.games.update({ctx.channel.id: {"ongoing": True}})

        start = time.time()

        await ctx.send(f"Timer game started! Type **now** in **{game_duration}** seconds.")

        progress = 0

        user_guesses = {}

        while progress <= game_duration:
            progress = time.time() - start - 2

            try:
                timeout = game_duration-progress

                message: discord.Message = await self.bot.wait_for("message", timeout=timeout, check=check)

            except asyncio.TimeoutError:
                # Game ended
                self.games.update({ctx.channel.id: {"ongoing": False}})

                # No participants
                if not user_guesses:
                    return await ctx.send(f"Timer game has ended with no winners")

                winner, guess = sorted(user_guesses.items(), key=lambda kv: abs(kv[1]))[0]

                text = "before" if guess < 0 else "after"

                with DBConnection() as con:
                    con.cur.execute(MinigamesSQL.UPDATE_TIMER_WINS, (winner.id,))

                await ctx.send(f"{winner.mention} has won! **{abs(guess)}s** {text} the timer.")

                return await self.timer_game(ctx)

            else:
                # New guess
                if message.author not in user_guesses:
                    user_guesses[message.author] = round(time.time() - start - game_duration, 3)

    @commands.command(name="tlb", help="Timer LB")
    async def leaderboard(self, ctx: commands.Context):
        if self.leaderboards.get(ctx.guild.id, None) is None:
            self.leaderboards[ctx.guild.id] = TimerLeaderboard(ctx.guild, self.bot)

        lb = self.leaderboards[ctx.guild.id]

        return await ctx.send(lb.get(ctx.author))


def setup(bot):
    bot.add_cog(Minigames(bot))
