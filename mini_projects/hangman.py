import random

STATES = [
    r'''
|---------
|
|
|
|
    ''',
    r'''
|---------
|        O
|
|
|
    ''',
    r'''
|---------
|        O
|        |
|
|
    ''',
    r'''
|---------
|        O
|        |\
|
|
    ''',
    r'''
|---------
|        O
|       /|\
|
|
    ''',
    r'''
|---------
|        O
|       /|\
|         \
|
    ''',
    r'''
|---------
|        O
|       /|\
|       / \
|
    '''
]

def fetch_wordlist(src: str = 'words.txt', delimeter: str = ' ') -> list[str]:
    with open(src, 'r') as f:
        return f.readline().split(delimeter)

def display_clues(secret_word: str, gussed_letters: str, blank_character: str = '-', fetch: bool = False) -> None | str:
    construction = ''.join([[blank_character, character][character in guessed_letters] for character in secret_word])
    
    if fetch:
        return construction
    print(construction)

def fetch_guess(guessed_letters: str) -> str:
    guess = input("Enter a guess: ")
    while len(guess) != 1 or guess in guessed_letters:
        guess = input("Enter a guess: ")

    return guess

def hangman(secret_word: str, lives: int = 6):
    LIVE_LIMIT = lives
    word = ''
    guessed_letters: str = ''
    while True:
        word = display_clues(secret_word, guessed_letters, fetch=True)
        print(STATES[LIVE_LIMIT-lives], word, sep='\n')

        if word == secret_word: break
        if lives == 0: break

        guess = fetch_guess(guessed_letters)
        guessed_letters += guess
        if guess not in secret_word:
            lives -= 1

    if lives == 0: print(f"You lose! The correct word was {secret_word}")
    elif word == secret_word: print("You won!")
    else: print("There seems to be a bug...")  # This should never get executed.

def main():
    wordlist: list[str] = fetch_wordlist()
    secret_word = random.choice(wordlist).lower()
    hangman(secret_word)

if __name__ == '__main__':
    main()
