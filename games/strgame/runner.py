"""
      ===== SMART RUNNER v.1.1a =====
      Copyright (C) 2019 IU7Games Team.

    - В этом модуле расположена универсальная функция запуска
      тестирования функций как strtok, так и split.
"""

from functools import reduce
import psutil

TESTS_REPEATS = 1
NUMBER_OF_TESTS = 1

def concat_strings(file):
    """
        Склеивание каждой строки файла в одну единственную строку,
        удаление символов окончания строки.
    """

    return reduce(lambda x, y: x + y[:-1], file) * 20000


def runner(tests_path, tests_runner):
    """
        Функция на вход принимает дирректорию путь к папке с тестами и
        функцию, запускающую тесты для strtok или split.
    """

    total_time = 0
    total_tests = 0

    for i in range(TESTS_REPEATS):
        file = open(tests_path + "/test_" + str((i % NUMBER_OF_TESTS) + 1) + ".txt", "r")
        test_data = concat_strings(file)

        print(psutil.virtual_memory())
        file.close()

        time, error_code, dispersion = tests_runner(test_data)

        if not error_code:
            total_tests += 1
        total_time += time

    return total_tests, total_time, dispersion
