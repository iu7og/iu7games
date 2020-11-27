"""
    ===== LIGHT R3463NT RUNNER v.1.1a =====

    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию reagent игрока для проверки
    на отсутствие segmentation fault, бесконечных циклов и так далее.
"""

import os
from games.reagent.reagent_runner import start_reagent_competition


def light_reagent_runner(player_lib_path):
    """
        Запуск стратегии игрока на полях 3х3 и 5х5.
    """

    start_reagent_competition([(player_lib_path, 0)], 3)
    print("\033[0;32mREAGENT GAME: 3х3 FIELD OKAY\033[0m")

    start_reagent_competition([(player_lib_path, 0)], 5)
    print("\033[0;32mREAGENT GAME: 5х5 FIELD OKAY\033[0m")


if __name__ == "__main__":
    light_reagent_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_r3463nt_lib.so")
