"""
      ===== LIGHT TEEN48 RUNNER v.1.0a =====
      Copyright (C) 2019 IU7Games Team.

      Данный ранер запускает стратегию teen48 игрока, для проверки на отсутствие
      segmentation fault и бесконечный цикл в стратегии игрока.
"""

from games.teen48.teen48_runner import start_teen48game_competition

def light_teen48_runner(player_lib_path):
    """
        Запуск стратегии игрока с тестовой стратегией на игровых полях 4x4 и 8x8,
        вывод итогового результата и количество очков, набранных игроком.
    """

    start_teen48game_competition([(player_lib_path, 0)], 4)
    print("TEEN48 GAME: 4x4 FIELD OKAY")

    start_teen48game_competition([(player_lib_path, 0)], 8)
    print("TEEN48 GAME: 8x8 FIELD OKAY")


if __name__ == "__main__":
    light_teen48_runner("./teen48lib.so")
