"""
      ===== LIGHT SEQUENCE RUNNER v.1.0b =====
      Copyright (C) 2019 - 2020 IU7Games Team.

      Запуск стратегии 7EQUEENCEGAME игрока, для проверки на отсутствие segmentation fault,
      бесконечных циклов и так далее.
"""

import os
from games.sequence.sequence_runner import start_sequence_game

def light_sequence_runner(player_lib_path):
    """
        Запуск стратегии игрока на тестовых значениях.
    """

    start_sequence_game([player_lib_path])
    print("\033[0;32mSEQUENCE GAME: OKAY\033[0m")


if __name__ == "__main__":
    light_sequence_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_7equeence_lib.so")
