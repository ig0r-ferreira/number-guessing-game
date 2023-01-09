from enum import Enum
from functools import wraps
from random import randint
from typing import Callable

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

LOGO = r"""
   ___                       _____ _                __                 _
  / _ \_   _  ___  ___ ___  /__   \ |__   ___    /\ \ \_   _ _ __ ___ | |__   ___ _ __
 / /_\/ | | |/ _ \/ __/ __|   / /\/ '_ \ / _ \  /  \/ / | | | '_ ` _ \| '_ \ / _ \ '__|
/ /_\\| |_| |  __/\__ \__ \  / /  | | | |  __/ / /\  /| |_| | | | | | | |_) |  __/ |
\____/ \__,_|\___||___/___/  \/   |_| |_|\___| \_\ \/  \__,_|_| |_| |_|_.__/ \___|_|

"""  # noqa: E501

MIN_VALUE, MAX_VALUE = 1, 100
console = Console()


class Difficulty(Enum):
    EASY = 10
    HARD = 5


def display_welcome() -> None:
    console.print(
        LOGO,
        'Welcome to the Number Guessing Game!',
        sep='\n',
        style='bright_green',
    )


def generate_number() -> int:
    console.print(
        f"I'm thinking of a number between {MIN_VALUE} and {MAX_VALUE}",
        end='\n\n',
    )
    return randint(MIN_VALUE, MAX_VALUE)


def choose_difficulty() -> Enum:
    chosen_mode = Prompt.ask(
        '[cyan]Choose a difficulty[/]',
        choices=[mode.name.lower() for mode in Difficulty],
    )
    return Difficulty[chosen_mode.upper()]


def avoid_value_out_of_range(min_value: int, max_value: int):
    def decorator(function: Callable[..., int]):
        @wraps(function)
        def wrapper() -> int:
            while True:
                result = function()
                if max_value >= result >= min_value:
                    return result
                console.print(
                    'The number is outside the defined range.', style='red'
                )

        return wrapper

    return decorator


def avoid_repeated_guesses(function: Callable[..., int]):
    guesses: list[int] = []

    @wraps(function)
    def wrapper() -> int:
        nonlocal guesses

        while True:
            result = function()
            if result not in guesses:
                guesses.append(result)
                return result

            console.print(
                'You already guessed that number. Try another.', style='red'
            )

    return wrapper


@avoid_value_out_of_range(MIN_VALUE, MAX_VALUE)
def read_user_guess() -> int:
    return IntPrompt.ask('[cyan]Make a guess[/]')


def check_guess(guess: int, target: int) -> bool:
    if guess == target:
        console.print('\nYou guessed right. Very well!', style='bright_green')
        return True

    console.print('Too high.' if guess > target else 'Too low.')
    return False


def play_game() -> None:
    display_welcome()

    target_number = generate_number()
    total_attempts = choose_difficulty().value
    read_non_repeated_user_guess = avoid_repeated_guesses(read_user_guess)

    for num in range(total_attempts, 0, -1):
        console.print(
            f'\nYou have {num} attempts remaining to guess the number.',
            style='#ffa500',
        )

        hit = check_guess(read_non_repeated_user_guess(), target_number)

        if hit:
            break
    else:
        console.print(
            '\nYour chances are over, you lost. '
            f'The answer is {target_number}.',
            style='yellow3',
        )


def main() -> None:
    try:
        while True:
            play_game()

            play_again = Confirm.ask('\n[cyan]Want to play again?[/]')

            if not play_again:
                break

            console.clear()
    except (KeyboardInterrupt, EOFError):
        console.print('\n^C')
    else:
        console.print('\nUntil next time!', style='bright_green')


if __name__ == '__main__':
    main()
