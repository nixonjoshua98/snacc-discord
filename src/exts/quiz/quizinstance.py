import csv
import discord
import dataclasses


@dataclasses.dataclass(frozen=True)
class Question:
    question: str
    answer: str
    options: list


class QuizInstance:
    def __init__(self, questions, *, timer):
        self.round_timer = timer
        self.questions = questions

    async def run(self, ctx):
        message = await ctx.send(embed=self.create_embed())

    def create_embed(self):
        embed = discord.Embed(title="Quiz")

        embed.add_field(name="Leaderboard", value="Empty")

        return embed

    @staticmethod
    def create_instance(file_path: str, *, timer):
        inst = None

        with open(file_path, "r") as fh:
            reader = csv.reader(fh)

            lines = tuple(map(lambda line: [ele.strip() for ele in line], reader))

            if QuizInstance.validate(lines):
                questions = QuizInstance.create_questions(lines)

                inst = QuizInstance(questions, timer=timer)

        return inst

    @staticmethod
    def validate(content):
        for line in content:
            if len(line) != 6 or line[1].upper() not in ("A", "B", "C", "D"):
                return False

        return True

    @staticmethod
    def create_questions(content):
        questions = []

        for line in content:
            question, answer, *options = line

            questions.append(Question(question, answer.upper(), options))

        return questions


