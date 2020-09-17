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

    start_travel_game([player_lib_path])
    print("\033[0;32mTRAVEL GAME: OKAY\033[0m")


if __name__ == "__main__":
    light_travel_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_tr4v31_lib.so")
