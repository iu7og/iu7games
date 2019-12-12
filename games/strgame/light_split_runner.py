"""
      ===== LIGHT SPLIT RUNNER v.1.0a =====
      Copyright (C) 2019 IU7Games Team.

      Данный ранер запускает функцию split игрока на определенных тестовых данных,
      для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.

"""

import ctypes
#from games.strgame.runner import concat_strings
from runner import concat_strings


WORDS_COUNT = 5200
MAX_LEN_WORD = 17

def create_c_objects(bytes_string):
    """
        Создание строки, матрицы и символа делителя в С для передачи в функцию.
    """

    c_string = ctypes.create_string_buffer(bytes_string)
    c_split_strings = [ctypes.create_string_buffer(b' ' * MAX_LEN_WORD) for i in range(WORDS_COUNT)]
    c_split_matrix = (ctypes.c_char_p * WORDS_COUNT)(*map(ctypes.addressof, c_split_strings))
    delim = ctypes.c_wchar(' ')

    return c_string, c_split_strings, c_split_matrix, delim


def light_split_runner(player_lib_path, tests_path):
    """
        Запуск split функции игрока, для проверки на segfault / бесконечный цикл.
    """

    player_lib = ctypes.CDLL(player_lib_path)
    file = open(tests_path + "/test_data.txt", "r")
    test_string = concat_strings(file)
    file.close()

    test_string = test_string.encode("utf-8")
    c_string, _, c_matrix, delim = create_c_objects(test_string)
    _ = player_lib.split(c_string, c_matrix, delim)

    print("SPLIT OK")


if __name__ == "__main__":
    light_split_runner("./split_lib.so", "tests/split")
