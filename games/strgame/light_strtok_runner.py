"""
      ===== LIGHT STRTOK RUNNER v.1.0a =====
      Copyright (C) 2019 IU7Games Team.

      Данный ранер запускает функцию strtok игрока на определенных тестовых данных,
      для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

import ctypes
from games.strgame.runner import concat_strings

DELIMITERS = " ,.;:"
NULL = 0


def create_c_objects(bytes_string):
    """
        Создание тестируемой строки и строки с символами делителями.
    """

    c_string = ctypes.create_string_buffer(bytes_string)
    c_delimiters = ctypes.create_string_buffer(DELIMITERS.encode("utf-8"))

    return c_string, c_delimiters


def light_strtok_runner(player_lib_path, tests_path):
    """
        Чтение строки из файла, запуск strtok функции игрока
    """

    player_lib = ctypes.CDLL(player_lib_path)
    player_lib.strtok.restype = ctypes.POINTER(ctypes.c_char)

    file = open(tests_path + "/test_data.txt", "r")
    test_strtok_string = concat_strings(file)
    file.close()

    c_string, c_delimiters = create_c_objects(test_strtok_string.encode("utf-8"))
    ptr = ctypes.cast(player_lib.strtok(c_string, c_delimiters), ctypes.c_char_p)

    while ptr.value is not None:
        ptr = ctypes.cast(player_lib.strtok(NULL, c_delimiters), ctypes.c_char_p)

    print("STRTOK OK")


if __name__ == "__main__":
    light_strtok_runner("./strtok_lib.so", "tests/strtok")
