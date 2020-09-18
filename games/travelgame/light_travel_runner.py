"""
    ===== LIGHT TR4V31 RUNNER v.1.1a =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию travel_game игрока для проверки
    на отсутствие segmentation fault, бесконечных циклов и так далее.
"""

import os
from games.travelgame.travel_runner import start_travel_game


def light_travel_runner(player_lib_path):
    """
        Запуск стратегии игрока на тестовых значениях.
    """

    solution, _, _ = start_travel_game([player_lib_path])[0]
    print(f"\033[0;32mTRAVELGAME: OKAY\033[0m\nSOLUTION: {'OK' if solution == 0 else 'FAIL'}")


if __name__ == "__main__":
    light_travel_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_tr4v31_lib.so")
