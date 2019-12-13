"""
      ===== LIGHT XOGAME RUNNER v.1.0a =====
      Copyright (C) 2019 IU7Games Team.

      Данный ранер запускает стратегию xogame игрока с тестовой стратегий,
      для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

from games.xogame.xo_runner import start_xogame_competition

def light_xo_runner(player_lib_path):
    """
        Запуск стратегии игрока с тестовой стратегией на игровых полях 3х3 и 5х5.
    """

    start_xogame_competition([(player_lib_path, 0), ("/usr/lib/test_xo_lib.so", 0)], 3)
    print("XO GAME: 3x3 FIELD OKAY")

    start_xogame_competition([(player_lib_path, 0), ("/usr/lib/test_xo_lib.so", 0)], 5)
    print("XO GAME: 5x5 FIELD OKAY")


if __name__ == "__main__":
    light_xo_runner("./test3.so")
