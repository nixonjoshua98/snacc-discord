import os
import enum
import time
import string
import random

import discord

from typing import Union


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

        if not self.valid_guess(guess):
            return None

        elif self.is_user_on_cooldown(message.author):
            return HangmanGuess.USER_ON_COOLDOWN

        self.participants.add(message.author.id)

        return self.check_guess(guess)

    def valid_guess(self, guess: str) -> bool:
        is_word_guess = len(guess) == len(self.hidden_word)
        is_letter_guess = len(guess) == 1 and guess in string.ascii_uppercase + string.digits

        return is_word_guess or is_letter_guess

    def check_guess(self, guess: str) -> HangmanGuess:
        if guess in self.letter_guesses:
            return HangmanGuess.ALREADY_GUESSED

        elif len(guess) == 1 and guess in self.hidden_word.upper():
            self.letter_guesses.add(guess)

            if self.check_win():
                return HangmanGuess.GAME_WON

            return HangmanGuess.CORRECT_GUESS

        elif guess.upper() == self.hidden_word.upper():
            return HangmanGuess.GAME_WON

        else:
            if len(guess) == 1:
                self.letter_guesses.add(guess)

                self.lives_remaining -= 1

                return HangmanGuess.GAME_OVER if self.is_game_over() else HangmanGuess.WRONG_GUESS

            return None

    async def show_game(self, dest):
        return await dest.send(f"`{self.encode_word()} [{self.lives_remaining}]`")

    def is_game_over(self):
        return self.lives_remaining <= 0

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
            dir_ = os.path.dirname(os.path.abspath(__file__))

            for root, dirs, files in os.walk(os.path.join(dir_, "words")):
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