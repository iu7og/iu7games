"""
    ===== LIGHT SPLIT RUNNER v.1.0b =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию split игрока на определенных тестовых данных,
    для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

import os
from games.strgame.split_runner import start_split


def light_split_runner(player_lib_path, tests_path):
    """
        Запуск функции split игрока используя основной раннер.
    """

    tests_failed, _, _ = start_split(player_lib_path, tests_path)

    print(f"\033[0;32mSPLIT OK\033[0m\nTESTS FAILED: {tests_failed}")


if __name__ == "__main__":
    light_split_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_split_lib.so", "/games/strgame/tests/split")
