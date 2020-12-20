"""
    ===== LIGHT W00DCUTT3R RUNNER v.1.0.a =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает стратегию woodcutter игрока,
    для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

import os
from games.woodcutter.woodcutter_runner import start_woodcutter_game

def light_woodcutter_runner(player_lib_path):
    """
        Запуск стратегии игрока с тестовой стратегией.
    """

    start_woodcutter_game(
        [(player_lib_path, 0), (player_lib_path, 0)])
    print("\033[0;32mWOODCUTTER: OKAY\033[0m")


if __name__ == "__main__":
    light_woodcutter_runner(f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_w00dcutt3r_lib.so")
