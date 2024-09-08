"""CODE CRACKER

    The Secret word is a random 5-letter word provided by https://random-word-api.herokuapp.com.
    You have 10 attempts to crack the code. The colored feedback shows if a letter is at the right spot, wrong spot
    but in the secret word or doesn't appear at all.
"""
import requests
import console
import unicodedata


COLOR_CODE = {
    'G': '🟩',
    'Y': '🟨',
    'X': '🟥',
    0: '⬜️',    # just for the start
}
WORD_LENGTH = 5
LANGUAGE = 'de'     # random-word-api supported languages 2024/09 ["de","fr","it","es","zh"]
MAX_ATTEMPTS = 10

def get_random_word():
    """Get a random 5-letter word via the random-word-api
    """
    try:
        S = requests.Session()
        URL = "https://random-word-api.herokuapp.com/word?length=5"
        PARAMS = {
            'length': 5,
            'lang': LANGUAGE,
            'number': 1,
        }
        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()

        # avoid 'ß' for it'd become 'ss' and add a 6th letter
        if 'ẞ' in DATA:
          DATA = get_random_word()

        return DATA[0].upper()
    except requests.RequestException as e:
        print(f"Ups, Problem mit der Random-Word-Api : {e}")
        return "ERROR"

def check_guess(secret_word, guess):
    # initialize
    feedback = ['X' for _ in secret_word]
    remainder = list(secret_word)

    # 'G' correct letters
    for i, (g, s) in enumerate(zip(guess, secret_word)):
        if g == s:
            feedback[i] = 'G'
            remainder[i] = None

    # 'Y' misplaced letters
    for i, g in enumerate(guess):
        if feedback[i] == 'X' and g in remainder:
            feedback[i] = 'Y'
            remainder[remainder.index(g)] = None

    return feedback

def print_feedback(feedback):
    print('\t', *[COLOR_CODE[i] for i in feedback])

def get_guess(attempt):
    while True:
        guess = input(f'{attempt}) \t').strip()

        # normalize so äöü count as 1 letter each
        guess = unicodedata.normalize('NFC', guess)

        if guess.isalpha() and len(guess) == WORD_LENGTH:
            return guess.upper()
        else:
            print(f'Nur Worte mit {WORD_LENGTH} Buchstaben sind erlaubt.')

def solved(feedback):
    return set(feedback) == {'G'}

def play_again():
    while True:
        answer = input('Willst du nochmal spielen? [J]a oder [N]ein:\t').strip()
        if answer.upper() == 'J':
            return True
        if answer.upper() == 'N':
            return False

if __name__ == "__main__":
    print(f'KNACK DEN CODE  ({LANGUAGE})\n')

    attempt = 1
    secret_word = get_random_word()
    print_feedback([0]*5)
    game_is_on = True

    while game_is_on:
        round_finished = False

        while not round_finished:
            guess = get_guess(attempt)
            feedback = check_guess(secret_word, guess)
            print_feedback(feedback)

            if solved(feedback):
                print('\nDu hast den Code geknackt!')
                round_finished = True

            if attempt == MAX_ATTEMPTS:
                print(f'\nZu schwer. Das Geheimwort lautet {secret_word}')
                round_finished = True

            attempt += 1

        if play_again():
            attempt = 1
            secret_word = get_random_word()
            console.clear()
            print(f'KNACK DEN CODE ({LANGUAGE})\n')
            print_feedback([0]*5)
            round_finished = False
        else:
            game_is_on = False

    console.clear()
