import os

import discord

from discord.ext import commands

from discord.ext.commands import BucketType

from src.common import checks
from src.common.converters import Range

from .quizinstance import QuizInstance


class Quiz(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @checks.snaccman_only()
    @commands.max_concurrency(1, BucketType.guild)
    @commands.command(name="quiz")
    async def start_quiz(self, ctx, timer: Range(15, 300) = 60):
        """ [Snacc] Start a quiz! """

        await ctx.send(
            "Please DM me with a `.csv` of the quiz with the following format...\n"
            "```question, answer (A-D), option A, option B, ...```"
        )

        def wait_for(message: discord.Message):
            return message.guild is None and message.author.id == ctx.author.id

        while True:
            msg: discord.Message = await ctx.bot.wait_for("message", check=wait_for)

            if msg.attachments:
                file: discord.Attachment = msg.attachments[0]

                path = os.path.join(os.getcwd(), "temp")

                os.makedirs(path, exist_ok=True)

                file_path = os.path.join(path, f"{hash(ctx)}.csv")

                await file.save(file_path)

                quiz = QuizInstance.create_instance(file_path, timer=timer)

                if quiz is None:
                    await msg.author.send("Invalid quiz file sent")
                    continue

                await ctx.send("Quiz starting...")

                return await quiz.run(ctx)

