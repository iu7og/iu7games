"""
    ===== LIGHT SPLIT RUNNER v.1.0b =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию split игрока на определенных тестовых данных,
    для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

import os
from games.strgame.split_runner import start_split
#import ctypes
#import games.utils.utils as utils


"""
WORDS_COUNT = 5200
MAX_LEN_WORD = 17

def create_c_objects(bytes_string):
        #Создание строки, матрицы и символа делителя в С для передачи в функцию.

    c_string = ctypes.create_string_buffer(bytes_string)
    c_split_strings = [ctypes.create_string_buffer(b' ' * MAX_LEN_WORD) for i in range(WORDS_COUNT)]
    c_split_matrix = (ctypes.c_char_p * WORDS_COUNT)(*map(ctypes.addressof, c_split_strings))
    delim = ctypes.c_wchar(' ')

    return c_string, c_split_strings, c_split_matrix, delim


def light_split_runner(player_lib_path, tests_path):
        #Чтение строки из файла, запуск split функции игрока

    utils.redirect_ctypes_stdout()

    player_lib = ctypes.CDLL(player_lib_path)
    file = open(tests_path + utils.TEST_FILE, "r")
    test_split_string = utils.concat_strings(file)
    file.close()

    c_string, _, c_matrix, delim = create_c_objects(test_split_string.encode(utils.ENCODING))
    _ = player_lib.split(c_string, c_matrix, delim)

    print("\033[0;32mSPLIT OK\033[0m")
"""

def light_split_runner(player_lib_path, tests_path):
    """
        Запуск функции split игрока используя основной раннер.
    """

    tests_failed, _, _ = start_split(palyer_lib_path, tests_path)

    print(f"\033[0;32mSPLIT OK\033[0m\nTESTS FAILED: {tests_failed}")

if __name__ == "__main__":
    light_split_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_split_lib.so", "/games/strgame/tests/split")
