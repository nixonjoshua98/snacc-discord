import discord
import enum

from datetime import datetime


class HangmanGuess(enum.IntEnum):
    GAME_WON = 0
    GAME_OVER = 1
    WRONG_GUESS = 2
    CORRECT_GUESS = 3
    ALREADY_GUESSED = 4
    USER_ON_COOLDOWN = 5


class HangmanGame:
    _all_words = set()

    def __init__(self):
        self.letter_guesses = set()
        self.cooldowns = dict()
        self.lives_remaining = 10

        self.hidden_word = self.get_new_word()

    def on_message(self, message: discord.Message):
        if self.is_user_on_cooldown(message.author):
            return HangmanGuess.USER_ON_COOLDOWN

        if not self.is_valid_guess(message.content):
            return None

        return self.check_guess(message.content.upper())

    async def show_game(self, dest):
        return await dest.send(f"`{self.encode_word()}` [{self.lives_remaining}]")

    def is_game_over(self):
        return self.lives_remaining <= 0

    def is_valid_guess(self, guess):
        return len(guess) == 1

    def is_user_on_cooldown(self, author: discord.Member) -> bool:
        cooldown = self.cooldowns.get(author.id, None)

        if cooldown is None or (datetime.now() - cooldown).total_seconds() >= 1:
            self.cooldowns[author.id] = datetime.now()

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
        if not HangmanGame._all_words:
            HangmanGame.load_all_words()

        return HangmanGame._all_words.pop()

    @staticmethod
    def load_all_words():
        with open("./bot/data/words.txt") as fh:
            HangmanGame._all_words = set(fh.read().splitlines())
