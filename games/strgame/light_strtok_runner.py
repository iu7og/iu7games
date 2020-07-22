"""
    ===== LIGHT STRTOK RUNNER v.1.0b =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию strtok игрока на определенных тестовых данных,
    для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

import os
from games.strgame.strtok_runner import start_strtok


def light_strtok_runner(player_lib_path, tests_path):
    """
        Запуск strtok функции используя основной раннер.
    """

    solution, _, _, = start_strtok(player_lib_path, tests_path)

    print(f"\033[0;32mSTRTOK OK\033[0m\nSOLUTION: {'OK' if solution == 0 else 'FAIL'")


if __name__ == "__main__":
    light_strtok_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_strtok_lib.so", "/games/strgame/tests/split")
