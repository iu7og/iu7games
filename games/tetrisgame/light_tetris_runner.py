"""
    ===== LIGHT T3TR15 RUNNER v.1.1a =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию tetris игрока для проверки
    на отсутствие segmentation fault, бесконечных циклов и так далее.
"""

import os
from games.tetrisgame.tetris_runner import start_tetris_competition


def light_tetris_runner(player_lib_path):
    """
        Запуск стратегии игрока.
    """

    start_tetris_competition([player_lib_path])
    print("\033[0;32mTETRIS GAME: OKAY\033[0m")


if __name__ == "__main__":
    light_tetris_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_t3tr15_lib.so")
