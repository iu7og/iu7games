"""
    ===== LIGHT STRTOK RUNNER v.1.0b =====
    Copyright (C) 2019 - 2020 IU7Games Team.

    Данный ранер запускает функцию strtok игрока на определенных тестовых данных,
    для проверки на отсутствие segmentation fault и бесконечный цикл в стратегии игрока.
"""

import os
from games.strgame.strtok_runner import start_strtok
#import games.utils.utils as utils

"""
def create_c_objects(bytes_string):
        #Создание тестируемой строки и строки с символами делителями.

    c_string = ctypes.create_string_buffer(bytes_string)
    c_delimiters = ctypes.create_string_buffer(utils.STRTOK_DELIMITERS.encode(utils.ENCODING))

    return c_string, c_delimiters


def light_strtok_runner(player_lib_path, tests_path):
        #Чтение строки из файла, запуск strtok функции игрока

    utils.redirect_ctypes_stdout()
    player_lib = ctypes.CDLL(player_lib_path)
    player_lib.strtok.restype = ctypes.POINTER(ctypes.c_char)

    file = open(tests_path + utils.TEST_FILE, "r")
    test_strtok_string = utils.concat_strings(file)
    file.close()

    c_string, c_delimiters = create_c_objects(test_strtok_string.encode(utils.ENCODING))
    ptr = ctypes.cast(player_lib.strtok(c_string, c_delimiters), ctypes.c_char_p)

    while ptr.value is not None:
        ptr = ctypes.cast(player_lib.strtok(utils.NULL, c_delimiters), ctypes.c_char_p)

    print("\033[0;32mSTRTOK OK\033[0m")
"""

def light_strtok_runner(player_lib_path, tests_path):
    """
        Запуск strtok функции используя основной раннер.
    """

    tests_failed, _, _, = start_strtok(player_lib_path, tests_path)

    print("\033[0;32mSTRTOK OK\033[0m\nTESTS FAILED: {tests_failed}")

if __name__ == "__main__":
    light_strtok_runner(
        f"/sandbox/{os.environ['GITLAB_USER_LOGIN']}_strtok_lib.so", "/games/strgame/tests/split")
