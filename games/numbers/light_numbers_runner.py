"""
    ===== LIGHT NUMBERS RUNNER v.1.0b =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Запуск стратегии NUM63RSGAME игрока, для проверки на отсутствие segmentation fault,
    бесконечных циклов и так далее.
"""

import os
from games.numbers.numbers_runner import start_numbers_game

def light_numbers_runner(player_lib_path):
    """
        Запуск стратегии игрока на тестовых значениях.
    """

    solution, _, _ = start_numbers_game([player_lib_path])[0]
    print(f"\033[0;32mNUMBERS GAME: OKAY\033[0m\nSOLUTION: {'OK' if solution == 0 else 'FAIL'}")


if __name__ == "__main__":
    light_numbers_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_num63rs_lib.so")
