import enum
import random
import string
import colorama

ANSWERS = 'answers.txt'
VALID_GUESSES = 'valid_guesses.txt'
SEED_SET = string.ascii_lowercase
BASE = len(SEED_SET)

with open(VALID_GUESSES, 'r') as f:
    VALID_GUESS_LIST = f.readlines()[0].strip().split()

GREEN = f"{colorama.Back.GREEN}{colorama.Fore.BLACK}"
YELLOW = f"{colorama.Back.YELLOW}{colorama.Fore.BLACK}"
DEFAULT = ""

class Difficulty(enum.Enum):
    EASY = 7
    MEDIUM = 5
    HARD = 3

    # You can easily add your own difficulties

    def __str__(self) -> str:
        return self.name
    
    def __int__(self) -> int:
        return self.value

def str_to_int(string: str) -> int:
    total: int = 0

    for i, char in enumerate(string[::-1]):
        total += BASE**(i) * SEED_SET.index(char)

    return total

def int_to_str(integer: int) -> str:
    construction: str = ''
    while integer:
        mod = integer % BASE
        construction += SEED_SET[mod]
        integer //= BASE
    
    return construction[::-1]

class Game:
    def __init__(self, difficulty: Difficulty = None, **kwargs) -> None:
        seed = kwargs.get('seed', "".join(random.choices(SEED_SET, k=5)))
        if not seed:
            seed = "".join(random.choices(SEED_SET, k=5))

        self.seed = seed

        self.__answer = self.fetch_answer()
        self.guesses = []
        self.difficulty = difficulty or Difficulty.MEDIUM
        self.chances = int(self.difficulty)

    def fetch_answer(self) -> str:
        with open(ANSWERS, 'r') as f:
            choices = f.readlines()[0].strip().split()
        random.seed(str_to_int(self.seed))
        return random.choice(choices)

    @property
    def answer(self) -> str:
        return self.__answer

    @staticmethod
    def fetch_difficulty() -> Difficulty:
        msg: str = "Choose your difficulty (Enter to skip):\n" + \
            '\n'.join([f'{i} {name} ({value.value} chances)' for i, (name, value) in enumerate(Difficulty._member_map_.items(), 1)]) + \
            '\n>>> '
        while True:
            try:
                choice = input(msg).strip()
                integer = int(choice)
                if not (0 < integer <= len(Difficulty._member_names_)):
                    raise KeyError
                
                return list(Difficulty._member_map_.values())[integer-1]
            except (ValueError, KeyError):
                if not choice:
                    return Difficulty.MEDIUM


    def play(self):
        def fetch_valid_guess(guessed_words: list[str]) -> str:
            while True:
                guess = input(f'Enter your guess ({self.chances} guesses left): ')
                upper = guess.upper()
                if len(guess) == 5 and guess.isalpha() and upper in VALID_GUESS_LIST and upper not in guessed_words:
                    return upper

        def display_correctness(guess: str) -> str:
            used = []
            for i, character in enumerate(guess):
                coloring = GREEN if character == self.answer[i] else \
                    YELLOW if character in self.answer and self.answer.count(character) != used.count(character) else \
                    DEFAULT
                
                print(f'{coloring}{character}{colorama.Style.RESET_ALL}', end='')
                used.append(character)
            print()
        
        guess: str = ''
        guessed_words: list[str] = []
        while guess != self.answer and self.chances > 0:
            guess = fetch_valid_guess(guessed_words)
            guessed_words.append(guess)
            display_correctness(guess)
            self.chances -= 1
        
        if guess == self.answer:
            print(f'You win! You got it in {self.difficulty.value-self.chances} guesses!')
        elif self.chances == 0:
            print(f'You lose! The word was {self.answer}')
        else:
            print("ERROR!")  # This shouldn't execute
        print(f'Your game code was : {self.seed!r}')

def main():
    game_code = code if (code := input('Enter a game code (if you have one, otherwise press enter): ')) else None
    difficulty = Game.fetch_difficulty()
    game = Game(difficulty=difficulty, seed=game_code)
    game.play()

if __name__ == '__main__':
    main()
